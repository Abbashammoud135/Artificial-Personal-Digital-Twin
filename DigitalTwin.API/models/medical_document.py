from datetime import datetime, timezone
import uuid


class MedicalDocument:

    def __init__(
        self,
        user_id: str,
        file_type: str,
        file_url: str,
        file_id: str = None,
        status: str = "uploaded"
    ):
        self.file_id = file_id if file_id else str(uuid.uuid4())
        self.user_id = user_id
        self.file_type = file_type
        self.file_url = file_url
        self.upload_time = datetime.now(timezone.utc)
        self.status = status

    def to_dict(self):
        return {
            "file_id": self.file_id,
            "user_id": self.user_id,
            "file_type": self.file_type,
            "file_url": self.file_url,
            "upload_time": self.upload_time,
            "status": self.status
        }