from agents.base import BaseAgent
from connectors.ollama.client import OllamaClient
from memory.qdrant.repository import QdrantRepository


class ContentAgent(BaseAgent):
    name = "content"

    def __init__(self) -> None:
        self.ollama = OllamaClient()
        self.rag = QdrantRepository()

    def run(self, context: dict) -> dict:
        references = self.rag.search(context.get("product", {}).get("title", "product"))
        prompt = f"Genera copy comercial breve usando contexto: {references}"
        draft = self.ollama.generate(prompt)
        return {"content": {"copy": draft, "references": references}}
