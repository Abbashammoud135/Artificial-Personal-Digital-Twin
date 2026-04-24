from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from models.base import Base

class Role(Base):
    __tablename__ = "Roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.getdate())

