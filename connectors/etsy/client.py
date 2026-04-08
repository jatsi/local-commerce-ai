from apps.api_gateway.app.core.config import settings

class EtsyConnector:
    def __init__(self):
        self.base_url = "https://api.etsy.com/v3"
        self.api_key = settings.etsy_api_key

    def create_draft_listing(self, payload: dict) -> dict:
        # Stub request aligned to Etsy Open API v3 style endpoints.
        return {
            "connector": "etsy",
            "status": "stub_ready",
            "action": "create_draft_listing",
            "endpoint": f"{self.base_url}/application/shops/{{shop_id}}/listings",
            "headers": {
                "x-api-key": self.api_key,
                "Authorization": "Bearer ***",
            },
            "payload": payload,
        }

    def update_listing(self, listing_id: str, payload: dict) -> dict:
        return {
            "connector": "etsy",
            "status": "stub_ready",
            "action": "update_listing",
            "listing_id": listing_id,
            "payload": payload,
        }
