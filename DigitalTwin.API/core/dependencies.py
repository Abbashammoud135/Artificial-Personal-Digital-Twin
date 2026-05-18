from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_token
from fastapi import Request
from sqlalchemy.orm import Session
from database.sqlserver.connection import sql_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login",scheme_name="BearerAuth")
bearer_scheme = HTTPBearer()
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = creds.credentials  
    payload = decode_token(token)
    print("PAYLOAD:", payload)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": payload["sub"],
        "email": payload["email"],
        "role_id": payload["role_id"]
    }

def get_health_profile_service(request: Request):
    return request.app.state.health_profile_service


def get_auth_service(request: Request):
    return request.app.state.auth_service

def get_medical_repo(request: Request):
    return request.app.state.medical_repo

def get_storage_service(request: Request):
    return request.app.state.storage_service

def get_db() -> Session:
    """Dependency injection for database sessions in endpoints"""
    db = sql_db.get_session()
    try:
        yield db
    finally:
        db.close()