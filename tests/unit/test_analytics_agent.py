from agents.analytics_agent.agent import AnalyticsAgent
from agents.analytics_agent.marketplace_discovery import MarketplaceDiscoveryClient


HTML = """
<html>
  <body>
    <a href="/dp/B001">Best Seller GPS Tracker Magnético para Auto</a>
    <span>$29.99</span>
    <a href="/listing/123">Collar Personalizado Top Ventas para Mascotas</a>
    <span>US$18.50</span>
    <a href="/products/gps-auto">Popular Mini GPS Tracker Waterproof</a>
    <span>$34.00</span>
  </body>
</html>
"""


def test_marketplace_discovery_extracts_products_from_html() -> None:
    client = MarketplaceDiscoveryClient()

    products = client._extract_products(
        html=HTML,
        marketplace="amazon",
        base_url="https://www.amazon.com/s?k=gps",
        max_products=2,
    )

    assert products[0]["title"] == "Best Seller GPS Tracker Magnético para Auto"
    assert products[0]["url"] == "https://www.amazon.com/dp/B001"
    assert products[0]["score"] > 1


def test_marketplace_discovery_uses_shopify_store_env(monkeypatch) -> None:
    monkeypatch.delenv("SHOPIFY_DISCOVERY_STORES", raising=False)
    monkeypatch.setenv("SHOPIFY_STORE", "demo.myshopify.com")

    client = MarketplaceDiscoveryClient()

    assert client._search_urls_for(
        marketplace="shopify",
        query="gps auto",
        marketplace_urls={},
        shopify_stores=None,
    ) == ["https://demo.myshopify.com/search?q=gps+auto"]


def test_analytics_agent_runs_automatic_marketplace_scraping(monkeypatch) -> None:
    def fake_discover(  # type: ignore[no-untyped-def]
        self, query, marketplaces, max_products, marketplace_urls, shopify_stores
    ):
        return [
            {
                "marketplace": marketplaces[0],
                "query": query,
                "search_url": "https://example.com/search?q=gps",
                "status": "scraped",
                "products": [
                    {
                        "title": "Best Seller GPS Tracker Magnético para Auto",
                        "url": "https://example.com/products/gps",
                        "price": 29.99,
                        "score": 3,
                    }
                ],
            }
        ]

    monkeypatch.setattr(MarketplaceDiscoveryClient, "discover", fake_discover)

    result = AnalyticsAgent().run(
        {
            "niches": ["gps auto"],
            "marketplaces": ["amazon", "etsy", "shopify", "mercadolibre"],
            "max_products_per_marketplace": 3,
        }
    )

    analytics = result["analytics"]
    assert analytics["automation"]["enabled"] is True
    assert analytics["automation"]["mode"] == "automatic_marketplace_scraping"
    assert analytics["automation"]["marketplaces"] == [
        "amazon",
        "etsy",
        "shopify",
        "mercadolibre",
    ]
    assert (
        analytics["best_sellers"][0]["title"]
        == "Best Seller GPS Tracker Magnético para Auto"
    )
    assert "tracker" in analytics["top_keywords"]
