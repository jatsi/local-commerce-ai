import httpx
from apps.api_gateway.app.core.config import settings

class ShopifyConnector:
    def __init__(self):
        self.base_url = f"https://{settings.shopify_store_domain}/admin/api/{settings.shopify_api_version}/graphql.json"
        self.headers = {
            "X-Shopify-Access-Token": settings.shopify_access_token,
            "Content-Type": "application/json",
        }

    def create_product(self, payload: dict) -> dict:
        # Stub request body aligned to Shopify Admin GraphQL's productCreate mutation.
        query = '''
        mutation productCreate($product: ProductCreateInput!) {
          productCreate(product: $product) {
            product { id title status }
            userErrors { field message }
          }
        }
        '''
        variables = {
            "product": {
                "title": payload.get("title", "Draft Shopify Product"),
                "status": "DRAFT",
                "descriptionHtml": payload.get("description_html", "<p>Generated locally</p>")
            }
        }
        return {
            "connector": "shopify",
            "status": "stub_ready",
            "action": "create_product",
            "endpoint": self.base_url,
            "query": query,
            "variables": variables,
        }

    def update_product(self, product_id: str, payload: dict) -> dict:
        return {
            "connector": "shopify",
            "status": "stub_ready",
            "action": "update_product",
            "product_id": product_id,
            "payload": payload,
        }
