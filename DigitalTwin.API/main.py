from fastapi import FastAPI
from contextlib import asynccontextmanager
import traceback

from database.mongo.connection import mongo
from database.sqlserver.connection import sql_db
from database.redis.connection import redis_db

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.health_profile import router as health_profile_router

from database.sqlserver.repositories.user_repo import UserRepository
from services.auth_service import AuthService

from seeds.role_seeds import seed_roles

from services.health_profile_service import HealthProfileService
from database.sqlserver.repositories.health_profile_repo import HealthProfileRepository
import os
# auth_service = None
# health_profile_service = None
print("🚀 MAIN APP RUNNING ON PORT")
print("PID:", os.getpid())

@asynccontextmanager
async def lifespan(app: FastAPI):
    global auth_service, health_profile_service
    # 🚀 Startup
    try:
        await mongo.connect()
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        
    try:
        sql_db.connect()
        print("✅ SQL Server connected")
    except Exception as e:
        print(f"❌ SQL Server connection failed: {e}")
        traceback.print_exc()
        
    try:
        redis_db.connect()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")

    print("🚀 System started (Mongo+SQL+Redis connected)")
    
    # 🧠 CREATE SQL SESSION
    try:
        session = sql_db.get_session()

        # 🗄️ REPOSITORY
        user_repo = UserRepository(session)

        # ⚙️ SERVICE
        auth_service = AuthService(user_repo)
        
        # 🧠 HEALTH PROFILE SERVICE
        health_profile_repo = HealthProfileRepository(session)
        health_profile_service = HealthProfileService(health_profile_repo)
        
        # 📌 attach to FastAPI app 
        app.state.auth_service = auth_service
        app.state.health_profile_service = health_profile_service

        app.state.db_session = session
        
        print("🔐 Auth service initialized")
        
        # 🌱 SEED ROLES
        seed_roles(session)
        print("✅ Roles seeded")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        traceback.print_exc()
    
    yield

    # 🛑 Shutdown
    try:
        session.close()
        mongo.close()
        sql_db.engine.dispose()
        redis_db.client.close()
        print("🛑 System stopped")
    except Exception as e:
        print(f"⚠️  Error during shutdown: {e}")


app = FastAPI(
    title="Digital Twin AI System",
    description="Multi-agent Personal AI System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(auth_router, prefix="/auth")
app.include_router(health_profile_router, prefix="/health-profile", tags=["Health Profile"])