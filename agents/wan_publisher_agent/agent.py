from agents.base import BaseAgent


class WanPublisherAgent(BaseAgent):
    name = "wan_publisher"

    def run(self, context: dict) -> dict:
        assets = context.get("wan_assets", [])
        channels = context.get("social_channels", ["youtube", "tiktok", "facebook_reels"])
        published = [
            {"asset": asset.get("asset"), "channels": channels, "status": "scheduled"}
            for asset in assets
        ]
        return {"social_distribution": published}
