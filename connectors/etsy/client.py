class EtsyClient:
    def publish_listing(self, payload: dict) -> dict:
        return {"status": "stub_ready", "channel": "etsy", "product": payload.get("product", {})}
