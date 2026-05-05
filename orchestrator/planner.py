from dataclasses import dataclass


@dataclass
class PlanStep:
    order: int
    agent: str
    action: str


class Planner:
    BASE_FLOW = [
        "niche_analytics",  # Agente 1
        "ads",              # Agente 2
        "shopify",          # Agente 3
        "email",            # Agente 5
        "wan_creator",      # Agente 6
        "wan_publisher",    # Agente 7
        "analytics",        # Cierre de performance
    ]

    def build(self, job_name: str) -> list[PlanStep]:
        return [PlanStep(order=i + 1, agent=a, action=f"{job_name}:{a}") for i, a in enumerate(self.BASE_FLOW)]
