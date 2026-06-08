from database.mongo.connection import mongo
from database.mongo.collections import Collections
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

class ActionRepository:
    def __init__(self):
        self.db = mongo.get_db()

    def _sanitize_document(self, doc):
        if not doc:
            return {}
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def _safe_object_id(self, id_str):
        try:
            return ObjectId(id_str)
        except (InvalidId, TypeError):
            return id_str

    # ==========================================
    # CALENDAR EVENTS
    # ==========================================
    async def save_calendar_event(self, user_id: str, event: dict) -> dict:
        collection = self.db[Collections.ACTION_CALENDAR_EVENTS]
        event_doc = {
            "user_id": user_id,
            "title": event.get("title"),
            "start": event.get("start"),
            "end": event.get("end"),
            "description": event.get("description"),
            "created_at": datetime.utcnow()
        }
        result = await collection.insert_one(event_doc)
        event_doc["_id"] = result.inserted_id
        return self._sanitize_document(event_doc)

    async def list_calendar_events(self, user_id: str) -> list:
        collection = self.db[Collections.ACTION_CALENDAR_EVENTS]
        cursor = collection.find({"user_id": user_id}).sort("start", 1)
        docs = await cursor.to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]

    async def update_calendar_event(self, user_id: str, event_id: str, updates: dict) -> dict:
        collection = self.db[Collections.ACTION_CALENDAR_EVENTS]
        query = {"_id": self._safe_object_id(event_id), "user_id": user_id}
        
        allowed_fields = ["title", "start", "end", "description"]
        update_doc = {"$set": {k: v for k, v in updates.items() if k in allowed_fields}}
        update_doc["$set"]["updated_at"] = datetime.utcnow()
        
        await collection.update_one(query, update_doc)
        updated_doc = await collection.find_one(query)
        return self._sanitize_document(updated_doc)

    async def delete_calendar_event(self, user_id: str, event_id: str) -> bool:
        collection = self.db[Collections.ACTION_CALENDAR_EVENTS]
        query = {"_id": self._safe_object_id(event_id), "user_id": user_id}
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    # ==========================================
    # EMAIL SENT HISTORY
    # ==========================================
    async def save_sent_email(self, user_id: str, email: dict) -> dict:
        collection = self.db[Collections.ACTION_SENT_EMAILS]
        email_doc = {
            "user_id": user_id,
            "to": email.get("to"),
            "subject": email.get("subject"),
            "body": email.get("body"),
            "sent_at": datetime.utcnow()
        }
        result = await collection.insert_one(email_doc)
        email_doc["_id"] = result.inserted_id
        return self._sanitize_document(email_doc)

    async def list_sent_emails(self, user_id: str) -> list:
        collection = self.db[Collections.ACTION_SENT_EMAILS]
        cursor = collection.find({"user_id": user_id}).sort("sent_at", -1)
        docs = await cursor.to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]

    # ==========================================
    # EMAIL DRAFTS
    # ==========================================
    async def save_email_draft(self, user_id: str, draft: dict) -> dict:
        collection = self.db[Collections.ACTION_EMAIL_DRAFTS]
        draft_doc = {
            "user_id": user_id,
            "to": draft.get("to"),
            "subject": draft.get("subject"),
            "body": draft.get("body"),
            "context": draft.get("context"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await collection.insert_one(draft_doc)
        draft_doc["_id"] = result.inserted_id
        return self._sanitize_document(draft_doc)

    async def list_email_drafts(self, user_id: str) -> list:
        collection = self.db[Collections.ACTION_EMAIL_DRAFTS]
        cursor = collection.find({"user_id": user_id}).sort("updated_at", -1)
        docs = await cursor.to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]

    async def get_email_draft(self, user_id: str, draft_id: str) -> dict:
        collection = self.db[Collections.ACTION_EMAIL_DRAFTS]
        query = {"_id": self._safe_object_id(draft_id), "user_id": user_id}
        doc = await collection.find_one(query)
        return self._sanitize_document(doc)

    async def update_email_draft(self, user_id: str, draft_id: str, updates: dict) -> dict:
        collection = self.db[Collections.ACTION_EMAIL_DRAFTS]
        query = {"_id": self._safe_object_id(draft_id), "user_id": user_id}
        
        allowed_fields = ["to", "subject", "body", "context"]
        clean_updates = {k: v for k, v in updates.items() if k in allowed_fields and v not in ["", None] }
        update_doc = {"$set": clean_updates}
        update_doc["$set"]["updated_at"] = datetime.utcnow()
        
        await collection.update_one(query, update_doc)
        updated_doc = await collection.find_one(query)
        return self._sanitize_document(updated_doc)

    async def delete_email_draft(self, user_id: str, draft_id: str) -> bool:
        collection = self.db[Collections.ACTION_EMAIL_DRAFTS]
        query = {"_id": self._safe_object_id(draft_id), "user_id": user_id}
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    # ==========================================
    # STYLE PROFILES
    # ==========================================
    async def get_style_profile(self, user_id: str, style_name: str = None) -> dict:
        collection = self.db[Collections.ACTION_STYLE_PROFILES]
        query = {"user_id": user_id}
        if style_name:
            query["style_name"] = style_name
        doc = await collection.find_one(query)
        # if not doc and style_name:
        #     # Fallback to general first style profile if specific one not found
        #     doc = await collection.find_one({"user_id": user_id})
        return self._sanitize_document(doc)

    async def list_style_profiles(self, user_id: str) -> list:
        collection = self.db[Collections.ACTION_STYLE_PROFILES]
        cursor = collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]

    async def save_style_profile(self, user_id: str, profile: dict) -> dict:
        collection = self.db[Collections.ACTION_STYLE_PROFILES]
        style_name = profile.get("style_name", "default")
        query = {"user_id": user_id, "style_name": style_name}
        
        update_doc = {
            "user_id": user_id,
            "style_name": style_name,
            "tone": profile.get("tone", "neutral"),
            "signature": profile.get("signature", ""),
            "formatting": profile.get("formatting", "paragraphs"),
            "recurring_phrases": profile.get("recurring_phrases", []),
            "updated_at": datetime.utcnow()
        }
        
        await collection.replace_one(query, update_doc, upsert=True)
        updated_doc = await collection.find_one(query)
        return self._sanitize_document(updated_doc)

    async def delete_style_profile(self, user_id: str, style_name: str) -> bool:
        collection = self.db[Collections.ACTION_STYLE_PROFILES]
        query = {"user_id": user_id, "style_name": style_name}
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    # ==========================================
    # NOTIFICATIONS
    # ==========================================
    async def save_notification(self, user_id: str, notification: dict) -> dict:
        collection = self.db[Collections.ACTION_NOTIFICATIONS]
        notif_doc = {
            "user_id": user_id,
            "message": notification.get("message"),
            "level": notification.get("level", "info"),
            "read": False,
            "created_at": datetime.utcnow()
        }
        result = await collection.insert_one(notif_doc)
        notif_doc["_id"] = result.inserted_id
        return self._sanitize_document(notif_doc)

    async def list_notifications(self, user_id: str) -> list:
        collection = self.db[Collections.ACTION_NOTIFICATIONS]
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [self._sanitize_document(doc) for doc in docs]
