from agents.base import BaseAgent


class NicheAnalyticsAgent(BaseAgent):
    name = "niche_analytics"

    def run(self, context: dict) -> dict:
        niches = context.get("niches", ["cosmeticos", "electronicos"])
        max_products = int(context.get("max_products_per_niche", 3))
        trending_products = {
            niche: [f"{niche}-trend-{i + 1}" for i in range(max_products)] for niche in niches
        }
        return {
            "niche_analysis": {
                "niches": niches,
                "trending_products": trending_products,
                "source": "marketplace+competitor_signals",
            }
        }
