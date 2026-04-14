import os

from agents.base import BaseAgent
from agents.competitor_agent.analyzer import CompetitorAnalyzer
from connectors.playwright_ops.client import PlaywrightClient


class CompetitorAgent(BaseAgent):
    name = "competitor"

    def __init__(self) -> None:
        self.scraper = PlaywrightClient()
        self.analyzer = CompetitorAnalyzer()

    def run(self, context: dict) -> dict:
        urls = context.get("competitor_urls") or self._urls_from_env()
        own_product = context.get("product", {})

        snapshots = [self.scraper.scrape(url) for url in urls]
        analysis = self.analyzer.analyze(snapshots=snapshots, own_product=own_product)

        return {
            "competitor": {
                "snapshots": snapshots,
                "analysis": analysis,
            }
        }

    def _urls_from_env(self) -> list[str]:
        raw = os.getenv("COMPETITOR_URLS", "")
        return [url.strip() for url in raw.split(",") if url.strip()]
