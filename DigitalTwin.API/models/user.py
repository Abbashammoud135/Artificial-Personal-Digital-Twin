from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from models.base import Base

class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("Roles.role_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.getdate())
    updated_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
