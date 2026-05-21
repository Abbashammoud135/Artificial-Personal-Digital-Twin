from datetime import datetime
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
        docs = await self.db[Collections.MEDICAL_DOCUMENTS].find(
            {"user_id": user_id}
        ).to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]

    def _sanitize_document(self, doc: dict):
        if not isinstance(doc, dict):
            return doc

        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        return doc

    async def update_report_analysis(self, file_id: str, analysis: dict):
        update_payload = {
            "analysis": analysis,
            "status": "analyzed",
            "analyzed_at": datetime.utcnow()
        }
        return await self.db[Collections.MEDICAL_DOCUMENTS].update_one(
            {"file_id": file_id},
            {"$set": update_payload}
        )