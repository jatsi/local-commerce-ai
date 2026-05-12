import pytest

from connectors.shopify.client import ShopifyClient, ShopifyConfigurationError


class FakeResponse:
    status_code = 201
    text = '{"product":{"id":123,"title":"Tracker Premium"}}'

    def json(self):
        return {"product": {"id": 123, "title": "Tracker Premium"}}


class FakeHttpClient:
    calls = []

    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def request(self, method, endpoint, headers, json):
        self.calls.append({"method": method, "endpoint": endpoint, "headers": headers, "json": json})
        return FakeResponse()


def test_shopify_client_builds_optimized_product_payload(monkeypatch) -> None:
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_store", "demo.myshopify.com")
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_access_token", "shpat_real")
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_api_version", "2026-01")

    client = ShopifyClient()
    payload = client._build_product_payload(
        {
            "niches": ["electronicos"],
            "product": {"title": "Tracker GPS", "price": 39.9, "sku": "GPS-1"},
            "content": {"copy": "Copy persuasivo generado por IA."},
            "product_marketing": {"title": "Tracker GPS Premium"},
        }
    )

    assert payload["title"] == "Tracker GPS Premium"
    assert payload["status"] == "active"
    assert "Copy persuasivo generado por IA." in payload["body_html"]
    assert payload["variants"] == [{"price": "39.9", "sku": "GPS-1"}]
    assert "electronicos" in payload["tags"]
    assert "ai-optimized" in payload["tags"]


def test_shopify_client_posts_to_real_shopify_endpoint(monkeypatch) -> None:
    FakeHttpClient.calls = []
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_store", "demo.myshopify.com")
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_access_token", "shpat_real")
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_api_version", "2026-01")
    monkeypatch.setattr("connectors.shopify.client.httpx.Client", FakeHttpClient)

    result = ShopifyClient().upsert_product({"product": {"title": "Tracker", "price": 29}})

    assert result["status"] == "published"
    assert result["product"]["id"] == 123
    assert FakeHttpClient.calls[0]["method"] == "POST"
    assert FakeHttpClient.calls[0]["endpoint"] == "https://demo.myshopify.com/admin/api/2026-01/products.json"
    assert FakeHttpClient.calls[0]["headers"]["X-Shopify-Access-Token"] == "shpat_real"
    assert FakeHttpClient.calls[0]["json"]["product"]["title"] == "Tracker"


def test_shopify_client_requires_real_credentials(monkeypatch) -> None:
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_store", "your-store.myshopify.com")
    monkeypatch.setattr("connectors.shopify.client.settings.shopify_access_token", "")

    with pytest.raises(ShopifyConfigurationError):
        ShopifyClient().upsert_product({"product": {"title": "Tracker"}})
