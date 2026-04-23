from database.mongo.connection import mongo
from database.mongo.collections import Collections

class MedicalRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def insert_report(self, report: dict):
        return await self.db[Collections.MEDICAL_DOCUMENTS].insert_one(report)

    async def get_user_reports(self, user_id: str):
        return await self.db[Collections.MEDICAL_DOCUMENTS].find(
            {"user_id": user_id}
        ).to_list(length=100)