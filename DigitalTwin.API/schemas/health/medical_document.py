from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MedicalDocumentResponse(BaseModel):
    file_id: str
    user_id: str
    file_type: str
    file_url: str
    upload_time: datetime
    status: str

    class Config:
        from_attributes = True