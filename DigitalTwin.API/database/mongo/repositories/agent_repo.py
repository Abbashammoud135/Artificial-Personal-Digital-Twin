from database.mongo.connection import mongo
from database.mongo.collections import Collections

class AgentRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def save_reasoning(self, data: dict):
        return await self.db[Collections.AGENT_REASONING].insert_one(data)