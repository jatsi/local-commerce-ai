from agents.base import BaseAgent


class EmailAgent(BaseAgent):
    name = "email"

    def run(self, context: dict) -> dict:
        inbox = context.get("inbox_messages", [])
        answered = [
            {"question": msg, "answer": "Gracias por escribirnos. Te respondemos con soporte comercial."}
            for msg in inbox
        ]
        return {"email_support": {"answered": answered, "count": len(answered)}}
