import os
import shutil
import uuid
from fastapi import UploadFile
from models.medical_document import MedicalDocument



class StorageService:

    UPLOAD_DIR = "uploads"

    def __init__(self, medical_repo):
        self.medical_repo = medical_repo
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    async def save_file(self, file: UploadFile, user_id: str) -> MedicalDocument:
        file_id = str(uuid.uuid4())

        file_path = os.path.join(self.UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_type = "pdf" if file.filename.endswith(".pdf") else "image"

        document = MedicalDocument(
            user_id=user_id,
            file_type=file_type,
            file_url=file_path
        )
        await self.medical_repo.insert_report(document)
        return document

    async def get_user_reports(self, user_id: str):
        return await self.medical_repo.get_user_reports(user_id)