from agents.base import BaseAgent
from connectors.google_ads.client import GoogleAdsClient
from connectors.meta_ads.client import MetaAdsClient


class AdsAgent(BaseAgent):
    name = "ads"

    def __init__(self) -> None:
        self.google = GoogleAdsClient()
        self.meta = MetaAdsClient()

    def run(self, context: dict) -> dict:
        campaign = context.get("campaign", {"name": "Launch", "budget": 100})
        return {
            "ads": {
                "google": self.google.create_campaign(campaign),
                "meta": self.meta.create_campaign(campaign),
            }
        }
