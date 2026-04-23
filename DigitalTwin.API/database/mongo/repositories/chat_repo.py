from database.mongo.connection import mongo
from database.mongo.collections import Collections

class ChatRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def save_conversation(self, convo: dict):
        return await self.db[Collections.CONVERSATIONS].insert_one(convo)

    async def get_history(self, user_id: str):
        return await self.db[Collections.CONVERSATIONS].find(
            {"user_id": user_id}
        ).to_list(length=50)