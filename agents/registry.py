from agents.ads_agent.agent import AdsAgent
from agents.analytics_agent.agent import AnalyticsAgent
from agents.catalog_agent.agent import CatalogAgent
from agents.competitor_agent.agent import CompetitorAgent
from agents.compliance_agent.agent import ComplianceAgent
from agents.content_agent.agent import ContentAgent
from agents.etsy_agent.agent import EtsyAgent
from agents.shopify_agent.agent import ShopifyAgent
from agents.web_agent.agent import WebAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents = {
            "catalog": CatalogAgent(),
            "content": ContentAgent(),
            "shopify": ShopifyAgent(),
            "etsy": EtsyAgent(),
            "web": WebAgent(),
            "competitor": CompetitorAgent(),
            "ads": AdsAgent(),
            "analytics": AnalyticsAgent(),
            "compliance": ComplianceAgent(),
        }

    def get(self, name: str):
        return self._agents[name]
