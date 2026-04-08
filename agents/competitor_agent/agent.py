from agents.base import BaseAgent
from connectors.playwright_ops.client import PlaywrightClient


class CompetitorAgent(BaseAgent):
    name = "competitor"

    def __init__(self) -> None:
        self.scraper = PlaywrightClient()

    def run(self, context: dict) -> dict:
        urls = context.get("competitor_urls", [])
        snapshots = [self.scraper.scrape(url) for url in urls]
        return {"competitor": snapshots}
