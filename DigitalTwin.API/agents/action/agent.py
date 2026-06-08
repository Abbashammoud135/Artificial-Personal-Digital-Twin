from agents.action.implementation import ActionImplementation
from agents.action.schema import ActionIntent

class ActionAgent:
    def __init__(self, services: dict = None):
        self.impl = ActionImplementation(services)

    async def run(self, user_id: str, intent: dict) -> dict:
        action = ActionIntent(**intent)
        return await self.impl.execute(user_id, action)

    async def parse_and_run(self, user_id: str, query: str) -> dict:
        return await self.impl.parse_and_execute(user_id, query)