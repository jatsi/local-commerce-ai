from agents.ads_agent.agent import AdsAgent
from agents.analytics_agent.agent import AnalyticsAgent
from agents.email_agent.agent import EmailAgent
from agents.niche_analytics_agent.agent import NicheAnalyticsAgent
from agents.shopify_agent.agent import ShopifyAgent
from agents.wan_creator_agent.agent import WanCreatorAgent
from agents.wan_publisher_agent.agent import WanPublisherAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents = {
            "niche_analytics": NicheAnalyticsAgent(),
            "ads": AdsAgent(),
            "shopify": ShopifyAgent(),
            "email": EmailAgent(),
            "wan_creator": WanCreatorAgent(),
            "wan_publisher": WanPublisherAgent(),
            "analytics": AnalyticsAgent(),
        }

    def get(self, name: str):
        return self._agents[name]
