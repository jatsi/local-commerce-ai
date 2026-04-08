def build_plan(job: dict) -> dict:
    task_type = job.get("task_type", "unknown")
    context = job.get("context", {})
    constraints = job.get("constraints", {})

    if task_type == "publish_product":
        return {
            "steps": [
                {"agent": "catalog_agent", "action": "build_master_record", "context": context, "constraints": constraints},
                {"agent": "compliance_agent", "action": "pre_publish_review", "context": {"require_approval": constraints.get("require_approval", True)}},
                {"agent": "shopify_agent", "action": "create_draft", "context": context, "constraints": constraints},
                {"agent": "etsy_agent", "action": "create_draft", "context": context, "constraints": constraints},
            ]
        }

    if task_type == "sync_product_channels":
        return {
            "steps": [
                {"agent": "shopify_agent", "action": "sync_product", "context": context, "constraints": constraints},
                {"agent": "etsy_agent", "action": "sync_product", "context": context, "constraints": constraints},
            ]
        }

    return {"steps": [{"agent": "catalog_agent", "action": "noop", "context": context, "constraints": constraints}]}
