from __future__ import annotations

from collections import Counter

from agents.base import BaseAgent
from agents.analytics_agent.marketplace_discovery import MarketplaceDiscoveryClient


class AnalyticsAgent(BaseAgent):
    name = "analytics"

    def __init__(self) -> None:
        self.discovery = MarketplaceDiscoveryClient()

    def run(self, context: dict) -> dict:
        queries = self._queries_from_context(context)
        max_products = int(context.get("max_products_per_marketplace", 5))
        marketplaces = context.get("marketplaces") or [
            "amazon",
            "etsy",
            "shopify",
            "mercadolibre",
        ]
        marketplace_urls = context.get("marketplace_urls") or {}
        shopify_stores = context.get("shopify_discovery_stores")

        marketplace_discovery = []
        for query in queries:
            marketplace_discovery.extend(
                self.discovery.discover(
                    query=query,
                    marketplaces=marketplaces,
                    max_products=max_products,
                    marketplace_urls=marketplace_urls,
                    shopify_stores=shopify_stores,
                )
            )

        products = [
            product
            for snapshot in marketplace_discovery
            for product in snapshot.get("products", [])
        ]

        return {
            "analytics": {
                "roas": context.get("roas", 2.1),
                "ctr": context.get("ctr", 0.042),
                "status": "tracked",
                "marketplace_discovery": marketplace_discovery,
                "best_sellers": self._rank_products(products),
                "top_keywords": self._top_keywords(products),
                "automation": {
                    "enabled": True,
                    "mode": "automatic_marketplace_scraping",
                    "marketplaces": marketplaces,
                    "queries": queries,
                },
            }
        }

    def _queries_from_context(self, context: dict) -> list[str]:
        if context.get("discovery_queries"):
            return [str(query) for query in context["discovery_queries"]]
        if context.get("niches"):
            return [str(niche) for niche in context["niches"]]
        product = context.get("product") or {}
        if product.get("title"):
            return [str(product["title"])]
        return ["productos tendencia"]

    def _rank_products(self, products: list[dict]) -> list[dict]:
        return sorted(
            products, key=lambda product: product.get("score", 0), reverse=True
        )[:10]

    def _top_keywords(self, products: list[dict]) -> list[str]:
        words: list[str] = []
        for product in products:
            for raw in product.get("title", "").lower().replace("-", " ").split():
                token = "".join(ch for ch in raw if ch.isalnum())
                if len(token) >= 4:
                    words.append(token)
        return [word for word, _ in Counter(words).most_common(10)]
