from orchestrator.planner import build_plan

def test_publish_plan_contains_shopify_and_etsy():
    plan = build_plan({"task_type": "publish_product", "context": {}, "constraints": {}})
    agents = [step["agent"] for step in plan["steps"]]
    assert "shopify_agent" in agents
    assert "etsy_agent" in agents
