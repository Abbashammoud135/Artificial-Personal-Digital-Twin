from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role_id: int

    is_active: bool
    is_verified: bool

    created_at: datetime
    last_login: Optional[datetime]