from orchestrator.planner import build_plan
from agents.catalog_agent.agent import CatalogAgent
from agents.shopify_agent.agent import ShopifyAgent
from agents.etsy_agent.agent import EtsyAgent
from agents.compliance_agent.agent import ComplianceAgent

def run_job(job: dict) -> dict:
    plan = build_plan(job)
    results = []

    catalog = CatalogAgent()
    compliance = ComplianceAgent()
    shopify = ShopifyAgent()
    etsy = EtsyAgent()

    for step in plan["steps"]:
        if step["agent"] == "catalog_agent":
            results.append(catalog.run(step))
        elif step["agent"] == "shopify_agent":
            results.append(shopify.run(step))
        elif step["agent"] == "etsy_agent":
            results.append(etsy.run(step))
        elif step["agent"] == "compliance_agent":
            results.append(compliance.run(step))
        else:
            results.append({"status": "skipped", "step": step})

    return {"job": job, "plan": plan, "results": results}
