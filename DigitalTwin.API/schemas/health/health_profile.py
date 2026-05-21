from enum import Enum
from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    nonbinary = "nonbinary"
    other = "other"
    unspecified = "unspecified"


class BloodTypeEnum(str, Enum):
    a_positive = "A+"
    a_negative = "A-"
    b_positive = "B+"
    b_negative = "B-"
    o_positive = "O+"
    o_negative = "O-"
    ab_positive = "AB+"
    ab_negative = "AB-"
    unknown = "unknown"


class HealthProfileBase(BaseModel):
    birthdate: Optional[date] = None
    gender: Optional[GenderEnum] = None

    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None

    blood_type: Optional[BloodTypeEnum] = None
    chronic_conditions: Optional[str] = None

    lifestyle: Optional[str] = None
    stress_level: Optional[int] = None
    sleep_hours: Optional[float] = None

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "birthdate": "1990-01-01",
                "gender": "female",
                "height": 170.5,
                "weight": 68.0,
                "bmi": 23.5,
                "blood_type": "O+",
                "chronic_conditions": "none",
                "lifestyle": "active",
                "stress_level": 3,
                "sleep_hours": 7.5
            }
        }


class HealthProfileCreate(HealthProfileBase):
    pass


class HealthProfileUpdate(HealthProfileBase):
    pass


class HealthProfileResponse(HealthProfileBase):
    health_profile_id: str
    user_id: str

    class Config:
        from_attributes = True
        use_enum_values = True