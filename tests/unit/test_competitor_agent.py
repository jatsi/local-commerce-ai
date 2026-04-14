from agents.competitor_agent.analyzer import CompetitorAnalyzer
from connectors.playwright_ops.client import PlaywrightClient


def test_competitor_analyzer_generates_recommendations() -> None:
    analyzer = CompetitorAnalyzer()
    snapshots = [
        {"status": "scraped", "title": "GPS Tracker with Real Time Alerts", "price": 39.99},
        {"status": "scraped", "title": "Mini GPS Tracker for Cars", "price": 34.5},
        {"status": "scraped", "title": "Magnetic Vehicle Tracker Waterproof", "price": 42.0},
    ]

    result = analyzer.analyze(snapshots=snapshots, own_product={"title": "Tracker básico", "price": 49.0})

    assert result["competitors_count"] == 3
    assert result["average_price"] == 38.83
    assert len(result["top_keywords"]) > 0
    assert len(result["recommendations"]) > 0


def test_playwright_client_extracts_title_and_price() -> None:
    client = PlaywrightClient()
    html = """
    <html>
      <head><title>Super GPS Tracker</title></head>
      <body><div>Now only $29.99 today</div></body>
    </html>
    """

    assert client._extract_title(html) == "Super GPS Tracker"
    assert client._extract_price(html) == 29.99
