from connectors.qdrant.client import get_qdrant_client
from apps.api_gateway.app.settings import settings


class QdrantRepository:
    def __init__(self) -> None:
        self.client = get_qdrant_client()
        self.collection = settings.qdrant_collection

    def search(self, query: str) -> list[dict]:
        # stub_ready; replace with vector embeddings pipeline.
        return [{"source": "knowledge_base", "snippet": f"context for {query}"}]
