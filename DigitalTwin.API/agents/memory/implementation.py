from datetime import datetime


class MemoryImplementation:

    def __init__(self, mongo_client):
        self.mongo = mongo_client

        # separate memory DB (raw storage)
        self.memory_db = mongo_client["memory_db"]
        self.memory_collection = self.memory_db["raw_memory"]

    # -------------------------
    # FETCH ANY COLLECTION RAW
    # -------------------------
    def fetch_collection(self, db_name: str, collection_name: str, query: dict = {}):
        collection = self.mongo[db_name][collection_name]
        return list(collection.find(query))

    # -------------------------
    # SAVE RAW MEMORY
    # -------------------------
    def save_memory(self, user_id: str, data: list, source: str):

        docs = []

        for item in data:
            docs.append({
                "user_id": user_id,
                "source": source,
                "data": item,
                "timestamp": datetime.utcnow()
            })

        if docs:
            self.memory_collection.insert_many(docs)

        return len(docs)

    # -------------------------
    # GET USER MEMORY
    # -------------------------
    def get_user_memory(self, user_id: str):
        return list(self.memory_collection.find({"user_id": user_id}))