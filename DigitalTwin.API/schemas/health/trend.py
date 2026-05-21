from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TrendPoint(BaseModel):
    date: datetime
    value: float
    status: Optional[str] = None


class LabTrend(BaseModel):
    test_name: str
    units: Optional[str] = None
    trend: str
    latest_value: float
    min: float
    max: float
    avg: float
    points: List[TrendPoint]


class TrendResponse(BaseModel):
    user_id: str
    trends: dict[str, LabTrend]