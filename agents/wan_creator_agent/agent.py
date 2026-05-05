from agents.base import BaseAgent


class WanCreatorAgent(BaseAgent):
    name = "wan_creator"

    def run(self, context: dict) -> dict:
        products = context.get("niche_analysis", {}).get("trending_products", {})
        ad_assets = [
            {"niche": niche, "product": product, "asset": f"wan_ad_{niche}_{idx + 1}.mp4"}
            for niche, items in products.items()
            for idx, product in enumerate(items)
        ]
        return {"wan_assets": ad_assets}
