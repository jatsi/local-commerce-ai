from connectors.shopify.client import ShopifyConnector

class ShopifyAgent:
    def __init__(self):
        self.client = ShopifyConnector()

    def run(self, step: dict) -> dict:
        if step.get("action") == "create_draft":
            return self.client.create_product({
                "title": "Draft Shopify Product",
                "status": "draft",
                "source": "shopify_agent"
            })
        return {"agent": "shopify_agent", "status": "noop"}
