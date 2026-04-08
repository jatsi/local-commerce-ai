from agents.base import BaseAgent
from connectors.web_cms.client import WebCMSClient


class WebAgent(BaseAgent):
    name = "web"

    def __init__(self) -> None:
        self.client = WebCMSClient()

    def run(self, context: dict) -> dict:
        return {"web": self.client.publish_product_page(context)}
