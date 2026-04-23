import os
import redis
from dotenv import load_dotenv

load_dotenv()

class RedisClient:
    def __init__(self):
        self.client = None

    def connect(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB")),
            decode_responses=True
        )

        # test connection
        self.client.ping()

        print("⚡ Redis connected")

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

redis_db = RedisClient()