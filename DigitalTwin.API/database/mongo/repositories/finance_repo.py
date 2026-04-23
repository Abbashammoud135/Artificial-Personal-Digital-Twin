from database.mongo.connection import mongo
from database.mongo.collections import Collections


class FinanceRepository:

    def __init__(self):
        self.db = mongo.get_db()

    # 💳 Insert transaction
    async def insert_transaction(self, transaction: dict):
        return await self.db["transactions"].insert_one(transaction)

    # 📊 Get user transactions
    async def get_user_transactions(self, user_id: str, limit: int = 100):
        return await self.db["transactions"].find(
            {"user_id": user_id}
        ).sort("timestamp", -1).to_list(length=limit)

    # 💰 Insert budget
    async def insert_budget(self, budget: dict):
        return await self.db["budgets"].insert_one(budget)

    # 📉 Get budgets
    async def get_user_budgets(self, user_id: str):
        return await self.db["budgets"].find(
            {"user_id": user_id}
        ).to_list(length=50)

    # 🧠 Save finance AI insight (overspending, savings advice)
    async def insert_finance_insight(self, insight: dict):
        return await self.db["financial_insights"].insert_one(insight)

    # 📊 Get insights
    async def get_finance_insights(self, user_id: str):
        return await self.db["financial_insights"].find(
            {"user_id": user_id}
        ).to_list(length=50)