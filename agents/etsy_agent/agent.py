from agents.base import BaseAgent
from connectors.etsy.client import EtsyClient


class EtsyAgent(BaseAgent):
    name = "etsy"

    def __init__(self) -> None:
        self.client = EtsyClient()

    def run(self, context: dict) -> dict:
        return {"etsy": self.client.publish_listing(context)}
