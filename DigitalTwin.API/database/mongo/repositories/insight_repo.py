from database.mongo.connection import mongo
from database.mongo.collections import Collections

class InsightRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def save_insight(self, insight: dict):
        return await self.db[Collections.USER_INSIGHTS].insert_one(insight)

    async def get_user_insights(self, user_id: str):
        return await self.db[Collections.USER_INSIGHTS].find(
            {"user_id": user_id}
        ).to_list(length=20)