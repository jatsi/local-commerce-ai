from memory.postgres.models import Policy


class PolicyEngine:
    def evaluate(self, db, agent: str, payload: dict) -> tuple[bool, str]:
        policies = db.query(Policy).filter(Policy.is_active.is_(True)).all()
        for policy in policies:
            blocked_agents = policy.rule.get("blocked_agents", [])
            max_budget = policy.rule.get("max_budget")
            if agent in blocked_agents:
                return False, f"blocked_by_policy:{policy.name}"
            if max_budget is not None and payload.get("budget", 0) > max_budget:
                return False, f"budget_exceeded:{policy.name}"
        return True, "ok"
