class MetaAdsClient:
    def create_campaign(self, payload: dict) -> dict:
        return {"status": "stub_ready", "platform": "meta_ads", "campaign": payload}
