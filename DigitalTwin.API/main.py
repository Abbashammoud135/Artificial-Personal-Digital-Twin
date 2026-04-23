from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.mongo.connection import mongo
from database.sqlserver.connection import sql_db
from database.redis.connection import redis_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 Startup
    await mongo.connect()
    sql_db.connect()
    redis_db.connect()

    print("🚀 System started (Mongo+SQL+Redis connected)")

    yield

    # 🛑 Shutdown
    mongo.close()
    sql_db.engine.dispose()
    redis_db.client.close()
    print("🛑 System stopped")


app = FastAPI(
    title="Digital Twin AI System",
    description="Multi-agent Personal AI System",
    version="1.0.0",
    lifespan=lifespan
)