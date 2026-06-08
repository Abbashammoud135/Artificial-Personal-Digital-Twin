from database.mongo.connection import mongo

class MemoryRepository:

    def __init__(self):
        self.db = mongo.get_db()

    async def search(self, query: dict):
        print("🔍 MemoryRepository.search - Query:", query)

        collection = self.db[query["collection"]]

        # Step 1: build cursor
        cursor = collection.find(query.get("filter", {}))

        # Step 2: sort (if exists)
        if query.get("sort"):
            field, direction = next(iter(query["sort"].items()))
            cursor = cursor.sort(field, direction)

        # Step 3: limit (if exists)
        if query.get("limit"):
            cursor = cursor.limit(query["limit"])

        # Step 4: fetch results (Motor async)
        docs = await cursor.to_list(length=query.get("limit", 100))
        print(f"✅ MemoryRepository.search - Found {len(docs)} documents")

        # Step 5: sanitize safely
        return [self._sanitize_document(doc) for doc in docs]

    def _sanitize_document(self, doc):
        if not doc:
            return {}

        # Convert Mongo ObjectId to string
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        return doc