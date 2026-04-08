from agents.base import BaseAgent


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def run(self, context: dict) -> dict:
        forbidden = ["medicinal claim", "guaranteed cure"]
        text = str(context)
        flagged = [word for word in forbidden if word in text.lower()]
        return {"compliance": {"approved": len(flagged) == 0, "flags": flagged}}
