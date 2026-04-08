class WebCMSClient:
    def publish_product_page(self, payload: dict) -> dict:
        return {"status": "stub_ready", "channel": "web", "slug": payload.get("product", {}).get("sku", "draft")}
