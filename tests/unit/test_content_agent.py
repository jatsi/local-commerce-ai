from agents.content_agent.agent import ContentAgent


class FakeOllama:
    def generate(self, prompt: str) -> str:
        return "Copy generado por Ollama para vender mejor."


class FakeRag:
    def search(self, query: str) -> list[dict]:
        return [{"source": "test", "snippet": query}]


def test_content_agent_uses_generated_marketing_copy() -> None:
    agent = ContentAgent.__new__(ContentAgent)
    agent.ollama = FakeOllama()
    agent.rag = FakeRag()

    result = agent.run({"product": {"title": "Tracker GPS"}})

    assert result["content"]["title"] == "Tracker GPS Premium"
    assert result["content"]["copy"] == "Copy generado por Ollama para vender mejor."
    assert result["product_marketing"]["title"] == "Tracker GPS Premium"
