from datetime import datetime
from database.mongo.connection import mongo
from database.mongo.collections import Collections

class MemoryRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def search(self, query: dict):
        print("🔍 MemoryRepository.search - Query:", query)

        collection = self.db[query["collection"]]

        # STEP 1: extract query parts
        filter_query = query.get("filter", {})
        projection = query.get("projection", None)

        # STEP 2: build cursor (NOW WITH PROJECTION FIX)
        cursor = collection.find(filter_query, projection)

        # STEP 3: sort (if exists)
        if query.get("sort"):
            field, direction = next(iter(query["sort"].items()))
            cursor = cursor.sort(field, direction)

        # STEP 4: limit (if exists)
        limit = query.get("limit")
        if limit:
            cursor = cursor.limit(limit)

        # STEP 5: fetch results (Motor async)
        docs = await cursor.to_list(length=limit or 100)

        print(f"✅ MemoryRepository.search - Found {len(docs)} documents")

        # STEP 6: sanitize safely
        return [self._sanitize_document(doc) for doc in docs]

    async def save_memory(self, user_id: str, memory_content: dict):
        print(f"💾 Saving memory insight to collection '{Collections.USERS_MEMORY}' for user '{user_id}'")
        collection = self.db[Collections.USERS_MEMORY]
        doc = {
            "user_id": user_id,
            "content": memory_content,
            "created_at": datetime.utcnow()
        }
        await collection.insert_one(doc)
        
        # Convert _id to string for serialization safety
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def _sanitize_document(self, doc):
        if not doc:
            return {}

        # Convert Mongo ObjectId to string
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        return doc
