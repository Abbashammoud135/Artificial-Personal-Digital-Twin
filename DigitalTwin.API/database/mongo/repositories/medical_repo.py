from database.mongo.connection import mongo
from database.mongo.collections import Collections
from models.medical_document import MedicalDocument

class MedicalRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def insert_report(self, report: MedicalDocument):
        print("Inserting report into MongoDB:", report.to_dict())
        return await self.db[Collections.MEDICAL_DOCUMENTS].insert_one(report.to_dict())

    async def get_user_reports(self, user_id: str):
        print("DB NAME:", self.db.name)
        return await self.db[Collections.MEDICAL_DOCUMENTS].find(
            {"user_id": user_id}
        ).to_list(length=100)