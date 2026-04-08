class ComplianceAgent:
    def run(self, step: dict) -> dict:
        constraints = step.get("context", {})
        requires_approval = bool(constraints.get("require_approval", True))
        return {
            "agent": "compliance_agent",
            "status": "ok",
            "action": step.get("action"),
            "decision": "requires_approval" if requires_approval else "approved_for_publish",
        }
