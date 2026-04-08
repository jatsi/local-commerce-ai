class BaseAgent:
    name = "base"

    def run(self, context: dict) -> dict:
        raise NotImplementedError
