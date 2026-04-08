from connectors.etsy.client import EtsyConnector

class EtsyAgent:
    def __init__(self):
        self.client = EtsyConnector()

    def run(self, step: dict) -> dict:
        if step.get("action") == "create_draft":
            return self.client.create_draft_listing({
                "title": "Draft Etsy Listing",
                "state": "draft",
                "source": "etsy_agent"
            })
        return {"agent": "etsy_agent", "status": "noop"}
