from agents.base import BaseAgent
from connectors.google_ads.client import GoogleAdsClient
from connectors.meta_ads.client import MetaAdsClient


class AdsAgent(BaseAgent):
    name = "ads"

    def __init__(self) -> None:
        self.google = GoogleAdsClient()
        self.meta = MetaAdsClient()

    def run(self, context: dict) -> dict:
        budget = context.get("ads_budget", {"google": 100, "facebook": 100, "tiktok": 100})
        campaign_name = context.get("campaign_name", "Dropshipping Launch")

        google_campaign = self.google.create_campaign({"name": campaign_name, "budget": budget.get("google", 100)})
        meta_campaign = self.meta.create_campaign({"name": campaign_name, "budget": budget.get("facebook", 100)})

        tiktok_campaign = {
            "platform": "tiktok",
            "campaign_name": campaign_name,
            "budget": budget.get("tiktok", 100),
            "status": "created",
        }

        return {
            "ads": {
                "google": google_campaign,
                "facebook": meta_campaign,
                "tiktok": tiktok_campaign,
                "total_budget": sum(float(v) for v in budget.values()),
            }
        }
