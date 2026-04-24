import uuid
from sqlalchemy import Column, String, Date, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class HealthProfile(Base):
    __tablename__ = "HealthProfile"

    health_profile_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)

    birthdate = Column(Date, nullable=True)
    gender = Column(String, nullable=True)

    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    blood_type = Column(String, nullable=True)
    chronic_conditions = Column(String, nullable=True)

    lifestyle = Column(String, nullable=True)
    stress_level = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)

    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="health_profile")