from agents.base import BaseAgent


class AnalyticsAgent(BaseAgent):
    name = "analytics"

    def run(self, context: dict) -> dict:
        return {"analytics": {"roas": 2.1, "ctr": 0.042, "status": "tracked"}}
