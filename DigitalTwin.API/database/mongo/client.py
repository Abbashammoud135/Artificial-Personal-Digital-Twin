from motor.motor_asyncio import AsyncIOMotorClient
import os

class MongoClient:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        uri = os.getenv("MONGO_URI")

        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.get_database("MONGO_URI")

        print("✅ MongoDB connected")

    def get_db(self):
        return self.db

    def close(self):
        if self.client:
            self.client.close()