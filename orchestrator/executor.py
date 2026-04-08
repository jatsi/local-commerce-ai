from sqlalchemy.orm import Session
from agents.registry import AgentRegistry
from memory.postgres.models import Approval, AuditLog, JobStep
from orchestrator.planner import Planner
from orchestrator.policy_engine import PolicyEngine


class Orchestrator:
    def __init__(self) -> None:
        self.planner = Planner()
        self.registry = AgentRegistry()
        self.policy = PolicyEngine()

    def run(self, job_name: str, payload: dict, db: Session, job_id: str) -> dict:
        plan = self.planner.build(job_name)
        context = payload.copy()
        executed = []

        for step in plan:
            allowed, reason = self.policy.evaluate(db=db, agent=step.agent, payload=context)
            step_model = JobStep(
                job_id=job_id,
                agent=step.agent,
                step_order=step.order,
                status="pending",
                input_data=context,
                output_data={},
            )
            db.add(step_model)
            db.commit()
            db.refresh(step_model)

            if not allowed:
                approval = Approval(job_id=job_id, step_id=step_model.id, status="pending")
                step_model.status = "waiting_approval"
                db.add(approval)
                db.add(AuditLog(entity_type="job_step", entity_id=step_model.id, action="approval_required", payload={"reason": reason}))
                db.commit()
                break

            result = self.registry.get(step.agent).run(context)
            context.update(result)
            step_model.status = "completed"
            step_model.output_data = result
            db.add(AuditLog(entity_type="job_step", entity_id=step_model.id, action="executed", payload=result))
            db.commit()
            executed.append({"agent": step.agent, "result": result})

        return {"job": job_name, "executed": executed, "context": context}
