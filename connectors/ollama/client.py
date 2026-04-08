import httpx
from apps.api_gateway.app.settings import settings


class OllamaClient:
    def generate(self, prompt: str) -> str:
        try:
            with httpx.Client(timeout=20) as client:
                response = client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception:
            return "stub_ready_content"
