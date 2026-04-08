from qdrant_client import QdrantClient
from apps.api_gateway.app.settings import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)
