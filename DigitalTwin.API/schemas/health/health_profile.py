from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid


class HealthProfileBase(BaseModel):
    birthdate: Optional[date] = None
    gender: Optional[str] = None

    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None

    blood_type: Optional[str] = None
    chronic_conditions: Optional[str] = None

    lifestyle: Optional[str] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None


class HealthProfileCreate(HealthProfileBase):
    pass


class HealthProfileUpdate(HealthProfileBase):
    pass


class HealthProfileResponse(HealthProfileBase):
    health_profile_id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True