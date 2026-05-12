from agents.content_agent.agent import ContentAgent


def test_content_agent_generates_local_marketing_copy_when_ollama_is_unavailable(monkeypatch) -> None:
    agent = ContentAgent()
    monkeypatch.setattr(agent.rag, "search", lambda query: [{"source": "test", "snippet": query}])
    monkeypatch.setattr(agent.ollama, "generate", lambda prompt: (_ for _ in ()).throw(RuntimeError("offline")))

    result = agent.run({"product": {"title": "Tracker GPS"}})

    assert result["content"]["title"] == "Tracker GPS Premium"
    assert "Tracker GPS" in result["content"]["copy"]
    assert result["product_marketing"]["title"] == "Tracker GPS Premium"
