from apps.api_gateway.app.settings import settings


class ShopifyClient:
    def __init__(self) -> None:
        self.base_url = f"https://{settings.shopify_store}"

    def upsert_product(self, payload: dict) -> dict:
        # stub_ready: payload mapping and authentication are predesigned.
        return {
            "status": "stub_ready",
            "channel": "shopify",
            "endpoint": f"{self.base_url}/admin/api/products",
            "product": payload.get("product", {}),
        }
