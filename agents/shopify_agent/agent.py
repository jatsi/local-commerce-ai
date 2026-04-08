from agents.base import BaseAgent
from connectors.shopify.client import ShopifyClient


class ShopifyAgent(BaseAgent):
    name = "shopify"

    def __init__(self) -> None:
        self.client = ShopifyClient()

    def run(self, context: dict) -> dict:
        return {"shopify": self.client.upsert_product(context)}
