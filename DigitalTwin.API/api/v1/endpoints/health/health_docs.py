import os
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, Depends
from core.dependencies import get_current_user, get_storage_service, get_medical_repo
from schemas.health.medical_document import MedicalDocumentResponse
from services.storage_service import StorageService
from database.mongo.repositories.medical_repo import MedicalRepository
from utils.helpers import create_note_document_helper as create_note_document
from core.pipeline.medical_pipeline import MedicalPipeline
router = APIRouter()


@router.post("/upload", response_model=MedicalDocumentResponse)
async def upload_medical_file(
    file: UploadFile = File(None),
    note: str = Form(None),
    user=Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
    repo: MedicalRepository = Depends(get_medical_repo)
):
    user_id = user["user_id"]

    # Case 1: File upload
    if file:
        document = await storage_service.save_file(file, user_id)
        return document.to_dict()

    # Case 2: Doctor note
    elif note:
        document = create_note_document(note, user_id)
        await repo.insert_report(document)
        return document.to_dict()

    return {"error": "No file or note provided"}

@router.get("/reports", response_model=list[MedicalDocumentResponse])
async def get_medical_reports(
    user=Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    user_id = user["user_id"]
    reports = await storage_service.get_user_reports(user_id)
    return [MedicalDocumentResponse(**report) for report in reports]

@router.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    pipeline = MedicalPipeline()
    # save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = pipeline.process_pdf(tmp_path)

        return {
            "success": True,
            "data": result
        }

    finally:
        os.remove(tmp_path)