from orchestrator.planner import Planner


def test_planner_builds_required_agents() -> None:
    plan = Planner().build("launch")
    agents = [step.agent for step in plan]
    assert agents == ["catalog", "competitor", "content", "compliance", "shopify", "etsy", "web", "ads", "analytics"]
