from agents.base import BaseAgent
from connectors.ollama.client import OllamaClient
from memory.qdrant.repository import QdrantRepository


class ContentAgent(BaseAgent):
    name = "content"

    def __init__(self) -> None:
        self.ollama = OllamaClient()
        self.rag = QdrantRepository()

    def run(self, context: dict) -> dict:
        product = self._product_from_context(context)
        title = product.get("title", "Producto destacado")
        references = self.rag.search(title)
        prompt = (
            "Genera copy comercial breve, claro y llamativo para Shopify. "
            f"Producto: {product}. Contexto de apoyo: {references}. "
            "Incluye una propuesta enfocada en beneficios, confianza y conversión."
        )
        copy = self._generate_copy(prompt=prompt, product=product)
        return {
            "content": {
                "title": self._optimized_title(title),
                "copy": copy,
                "references": references,
            },
            "product_marketing": {
                "title": self._optimized_title(title),
            },
        }

    def _generate_copy(self, prompt: str, product: dict) -> str:
        try:
            generated = self.ollama.generate(prompt).strip()
        except Exception:
            generated = ""
        if generated:
            return generated
        title = product.get("title", "este producto")
        return (
            f"Descubre {title}: una opción práctica, atractiva y lista para elevar tu experiencia diaria. "
            "Su presentación está pensada para explicar beneficios rápido, generar confianza y motivar la compra."
        )

    @staticmethod
    def _optimized_title(title: str) -> str:
        clean_title = title.strip() or "Producto destacado"
        if any(word in clean_title.lower() for word in ("premium", "pro", "oferta")):
            return clean_title
        return f"{clean_title} Premium"

    @staticmethod
    def _product_from_context(context: dict) -> dict:
        product = context.get("product") or {}
        if isinstance(product, str):
            return {"title": product}
        if product:
            return dict(product)

        trending = context.get("niche_analysis", {}).get("trending_products", {})
        for niche, items in trending.items():
            if items:
                return {"title": str(items[0]).replace("-", " ").title(), "product_type": str(niche)}
        return {"title": "Producto destacado"}
