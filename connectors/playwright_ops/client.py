import re
from html.parser import HTMLParser

from urllib.error import URLError
from urllib.request import Request, urlopen


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


class PlaywrightClient:
    """Cliente de scraping ligero.

    Usa descarga HTML vía httpx y parseo simple para poder ejecutarse localmente
    sin inicializar Playwright en pruebas. Se mantiene el nombre del conector para
    conservar el contrato interno.
    """

    PRICE_PATTERN = re.compile(r"(?:\$|USD\s?)(\d+[\.,]?\d*)")

    def scrape(self, url: str) -> dict:
        html = self._fetch_html(url)
        if not html:
            return {"url": url, "title": "", "price": None, "status": "error"}

        title = self._extract_title(html)
        price = self._extract_price(html)
        return {
            "url": url,
            "title": title,
            "price": price,
            "status": "scraped",
        }

    def _fetch_html(self, url: str) -> str:
        try:
            request = Request(url, headers={"User-Agent": "local-commerce-ai/1.0"})
            with urlopen(request, timeout=15) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (URLError, TimeoutError, ValueError):
            return ""

    def _extract_title(self, html: str) -> str:
        parser = _TitleParser()
        parser.feed(html)
        return parser.title.strip()

    def _extract_price(self, html: str) -> float | None:
        match = self.PRICE_PATTERN.search(html)
        if not match:
            return None
        value = match.group(1).replace(",", "")
        try:
            return float(value)
        except ValueError:
            return None
