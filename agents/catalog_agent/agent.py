from agents.base import BaseAgent


class CatalogAgent(BaseAgent):
    name = "catalog"

    def run(self, context: dict) -> dict:
        product = context.get("product", {})
        return {"catalog": {"normalized": True, "sku": product.get("sku", "sku-stub")}}
