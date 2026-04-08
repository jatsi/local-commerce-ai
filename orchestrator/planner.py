from dataclasses import dataclass


@dataclass
class PlanStep:
    order: int
    agent: str
    action: str


class Planner:
    BASE_FLOW = [
        "catalog",
        "content",
        "compliance",
        "shopify",
        "etsy",
        "web",
        "ads",
        "analytics",
    ]

    def build(self, job_name: str) -> list[PlanStep]:
        return [PlanStep(order=i + 1, agent=a, action=f"{job_name}:{a}") for i, a in enumerate(self.BASE_FLOW)]
