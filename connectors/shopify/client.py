from __future__ import annotations

from html import escape
from typing import Any
from urllib.parse import urlparse

import httpx

from apps.api_gateway.app.settings import settings


class ShopifyConfigurationError(RuntimeError):
    pass


class ShopifyRequestError(RuntimeError):
    pass


class ShopifyClient:
    def __init__(self) -> None:
        self.store_domain = self._normalize_store_domain(settings.shopify_store)
        self.api_version = settings.shopify_api_version
        self.access_token = settings.shopify_access_token
        self.base_url = f"https://{self.store_domain}"

    def upsert_product(self, payload: dict) -> dict:
        self._validate_configuration()

        product_payload = self._build_product_payload(payload)
        source_product = payload.get("product") if isinstance(payload.get("product"), dict) else {}
        product_id = payload.get("shopify_product_id") or source_product.get("shopify_product_id")
        method = "PUT" if product_id else "POST"
        path = f"products/{product_id}.json" if product_id else "products.json"
        endpoint = f"{self.base_url}/admin/api/{self.api_version}/{path}"

        with httpx.Client(timeout=30) as client:
            response = client.request(
                method,
                endpoint,
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Access-Token": self.access_token,
                },
                json={"product": product_payload},
            )

        if response.status_code >= 400:
            raise ShopifyRequestError(
                f"Shopify rejected {method} {endpoint} with status {response.status_code}: {response.text[:500]}"
            )

        body = response.json()
        return {
            "status": "updated" if product_id else "published",
            "channel": "shopify",
            "endpoint": endpoint,
            "product": body.get("product", body),
            "request_product": product_payload,
        }

    def _validate_configuration(self) -> None:
        if not self.store_domain or "stub" in self.store_domain or self.store_domain == "your-store.myshopify.com":
            raise ShopifyConfigurationError("Configure SHOPIFY_STORE with the real .myshopify.com store domain.")
        if not self.access_token or self.access_token == "replace_me":
            raise ShopifyConfigurationError("Configure SHOPIFY_ACCESS_TOKEN with a Shopify Admin API access token.")

    @staticmethod
    def _normalize_store_domain(raw_domain: str) -> str:
        domain = (raw_domain or "").strip()
        if not domain:
            return domain
        parsed = urlparse(domain if "://" in domain else f"https://{domain}")
        return parsed.netloc.rstrip("/")

    def _build_product_payload(self, context: dict) -> dict:
        product = self._product_from_context(context)
        content = context.get("content", {})
        marketing = context.get("product_marketing", {})

        title = marketing.get("title") or content.get("title") or product.get("title") or product.get("name")
        if not title:
            raise ValueError("Shopify product publication needs a product title or niche trend.")

        body_html = (
            product.get("body_html")
            or product.get("html_description")
            or marketing.get("body_html")
            or content.get("body_html")
            or self._default_body_html(product, content, title)
        )

        shopify_product: dict[str, Any] = {
            "title": title,
            "body_html": body_html,
            "status": product.get("status", context.get("shopify_status", "active")),
            "tags": self._tags(context, product),
        }

        for source_key, target_key in (
            ("vendor", "vendor"),
            ("product_type", "product_type"),
            ("handle", "handle"),
            ("template_suffix", "template_suffix"),
            ("published_scope", "published_scope"),
        ):
            if product.get(source_key):
                shopify_product[target_key] = product[source_key]

        variant = self._variant(product)
        if variant:
            shopify_product["variants"] = [variant]

        images = self._images(product)
        if images:
            shopify_product["images"] = images

        return shopify_product

    def _product_from_context(self, context: dict) -> dict:
        product = context.get("product") or {}
        if isinstance(product, str):
            return {"title": product}
        if product:
            return dict(product)

        trending = context.get("niche_analysis", {}).get("trending_products", {})
        for niche, items in trending.items():
            if items:
                return {"title": str(items[0]).replace("-", " ").title(), "product_type": str(niche)}
        return {}

    def _default_body_html(self, product: dict, content: dict, title: str) -> str:
        copy = content.get("copy") or product.get("description") or f"{title} listo para destacar en tu tienda."
        benefits = product.get("benefits") or [
            "Diseño pensado para captar atención desde el primer vistazo.",
            "Descripción clara enfocada en beneficios y decisión de compra.",
            "Presentación optimizada para una experiencia de compra confiable.",
        ]
        benefits_html = "".join(f"<li>{escape(str(benefit))}</li>" for benefit in benefits)
        return (
            f"<section class='ai-product-hero'><h2>{escape(title)}</h2>"
            f"<p>{escape(str(copy))}</p></section>"
            f"<section class='ai-product-benefits'><h3>Por qué te va a encantar</h3>"
            f"<ul>{benefits_html}</ul></section>"
        )

    @staticmethod
    def _tags(context: dict, product: dict) -> str:
        raw_tags = product.get("tags", [])
        tags = (
            raw_tags
            if isinstance(raw_tags, list)
            else [tag.strip() for tag in str(raw_tags).split(",") if tag.strip()]
        )
        tags.extend(context.get("niches", []))
        tags.extend(["ai-optimized", "shopify"])
        return ", ".join(dict.fromkeys(str(tag) for tag in tags if tag))

    @staticmethod
    def _variant(product: dict) -> dict:
        variant: dict[str, Any] = {}
        if product.get("price") is not None:
            variant["price"] = str(product["price"])
        if product.get("compare_at_price") is not None:
            variant["compare_at_price"] = str(product["compare_at_price"])
        if product.get("sku"):
            variant["sku"] = product["sku"]
        if product.get("inventory_quantity") is not None:
            variant["inventory_quantity"] = int(product["inventory_quantity"])
        return variant

    @staticmethod
    def _images(product: dict) -> list[dict]:
        images = []
        if product.get("image_url"):
            images.append({"src": product["image_url"]})
        for image in product.get("images", []):
            if isinstance(image, str):
                images.append({"src": image})
            elif isinstance(image, dict) and image.get("src"):
                images.append({"src": image["src"], **({"alt": image["alt"]} if image.get("alt") else {})})
        return images
