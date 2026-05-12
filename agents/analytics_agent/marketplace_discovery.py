from __future__ import annotations

import os
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from urllib.parse import quote_plus, urljoin
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Marketplace:
    name: str
    search_url: str
    product_url_markers: tuple[str, ...]


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.lower() != "a":
            return
        attrs_dict = {name.lower(): value for name, value in attrs if value}
        href = attrs_dict.get("href")
        if href:
            self._current_href = href
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href:
            text = " ".join(" ".join(self._current_text).split())
            if text:
                self.anchors.append(
                    {"href": self._current_href, "text": unescape(text)}
                )
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_text.append(data)


class MarketplaceDiscoveryClient:
    """Descubre productos vendidos/tendencia en marketplaces públicos.

    El cliente construye búsquedas automáticamente para Amazon, Etsy y
    MercadoLibre. Para Shopify usa storefronts configurados porque Shopify es
    una plataforma de tiendas y no un marketplace único; se pueden pasar en el
    contexto o en ``SHOPIFY_DISCOVERY_STORES``.
    """

    DEFAULT_MARKETPLACES = {
        "amazon": Marketplace(
            name="amazon",
            search_url="https://www.amazon.com/s?k={query}&s=review-rank",
            product_url_markers=("/dp/", "/gp/product/"),
        ),
        "etsy": Marketplace(
            name="etsy",
            search_url="https://www.etsy.com/search?q={query}",
            product_url_markers=("/listing/",),
        ),
        "mercadolibre": Marketplace(
            name="mercadolibre",
            search_url="https://listado.mercadolibre.com/{query}",
            product_url_markers=("/p/", "MLA-", "MLM-", "MLB-", "MCO-", "MLC-", "MPE-"),
        ),
    }

    PRICE_PATTERN = re.compile(r"(?:US\$|USD\s?|\$)\s?(\d+[\.,]?\d*)")

    def discover(
        self,
        query: str,
        marketplaces: list[str] | None = None,
        max_products: int = 5,
        marketplace_urls: dict[str, str] | None = None,
        shopify_stores: list[str] | None = None,
    ) -> list[dict]:
        results: list[dict] = []
        enabled = marketplaces or ["amazon", "etsy", "shopify", "mercadolibre"]

        for marketplace_name in enabled:
            marketplace = marketplace_name.lower().strip()
            search_urls = self._search_urls_for(
                marketplace=marketplace,
                query=query,
                marketplace_urls=marketplace_urls or {},
                shopify_stores=shopify_stores,
            )
            for search_url in search_urls:
                html = self._fetch_html(search_url)
                if not html:
                    results.append(
                        {
                            "marketplace": marketplace,
                            "query": query,
                            "search_url": search_url,
                            "status": "error",
                            "products": [],
                        }
                    )
                    continue

                products = self._extract_products(
                    html=html,
                    marketplace=marketplace,
                    base_url=search_url,
                    max_products=max_products,
                )
                results.append(
                    {
                        "marketplace": marketplace,
                        "query": query,
                        "search_url": search_url,
                        "status": "scraped",
                        "products": products,
                    }
                )
        return results

    def _search_urls_for(
        self,
        marketplace: str,
        query: str,
        marketplace_urls: dict[str, str],
        shopify_stores: list[str] | None,
    ) -> list[str]:
        if marketplace in marketplace_urls:
            return [marketplace_urls[marketplace].format(query=quote_plus(query))]

        if marketplace == "shopify":
            stores = shopify_stores or self._shopify_stores_from_env()
            return [self._shopify_search_url(store, query) for store in stores]

        config = self.DEFAULT_MARKETPLACES.get(marketplace)
        if not config:
            return []
        return [config.search_url.format(query=quote_plus(query))]

    def _fetch_html(self, url: str) -> str:
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; local-commerce-ai/1.0; +https://local)"
                    ),
                    "Accept-Language": "es,en;q=0.8",
                },
            )
            with urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (URLError, TimeoutError, ValueError):
            return ""

    def _extract_products(
        self, html: str, marketplace: str, base_url: str, max_products: int
    ) -> list[dict]:
        parser = _AnchorParser()
        parser.feed(html)
        markers = self._markers_for(marketplace)
        products: list[dict] = []
        seen_urls: set[str] = set()

        for anchor in parser.anchors:
            href = anchor["href"]
            title = self._clean_title(anchor["text"])
            if not self._looks_like_product(href, title, markers):
                continue
            url = urljoin(base_url, href)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            products.append(
                {
                    "title": title,
                    "url": url,
                    "price": self._extract_nearby_price(html, href),
                    "score": self._score_title(title),
                }
            )
            if len(products) >= max_products:
                break
        return products

    def _markers_for(self, marketplace: str) -> tuple[str, ...]:
        if marketplace == "shopify":
            return ("/products/",)
        config = self.DEFAULT_MARKETPLACES.get(marketplace)
        return (
            config.product_url_markers
            if config
            else ("/products/", "/listing/", "/dp/")
        )

    def _looks_like_product(
        self, href: str, title: str, markers: tuple[str, ...]
    ) -> bool:
        return len(title) >= 12 and any(marker in href for marker in markers)

    def _clean_title(self, title: str) -> str:
        cleaned = " ".join(title.replace("\n", " ").split())
        return cleaned[:180]

    def _extract_nearby_price(self, html: str, href: str) -> float | None:
        position = html.find(href)
        if position == -1:
            return None
        window = html[max(0, position - 1500) : position + 1500]
        match = self.PRICE_PATTERN.search(window)
        if not match:
            return None
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return None

    def _score_title(self, title: str) -> int:
        title_lower = title.lower()
        score = 1
        for signal in (
            "best seller",
            "más vendido",
            "mas vendido",
            "popular",
            "top",
            "trending",
        ):
            if signal in title_lower:
                score += 2
        return score

    def _shopify_stores_from_env(self) -> list[str]:
        raw = os.getenv("SHOPIFY_DISCOVERY_STORES", "")
        stores = [store.strip() for store in raw.split(",") if store.strip()]
        primary_store = os.getenv("SHOPIFY_STORE", "").strip()
        if primary_store and primary_store not in stores:
            stores.append(primary_store)
        return stores

    def _shopify_search_url(self, store: str, query: str) -> str:
        normalized_store = store.strip().rstrip("/")
        if not normalized_store.startswith(("http://", "https://")):
            normalized_store = f"https://{normalized_store}"
        return f"{normalized_store}/search?q={quote_plus(query)}"
