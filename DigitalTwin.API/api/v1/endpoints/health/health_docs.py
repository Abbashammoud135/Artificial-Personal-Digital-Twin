import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from core.dependencies import (
    get_current_user,
    get_storage_service,
    get_medical_repo,
    get_agent_repo,
    get_rag_service
)
from schemas.health.medical_document import MedicalDocumentResponse
from services.storage_service import StorageService
from database.mongo.repositories.medical_repo import MedicalRepository
from database.mongo.repositories.agent_repo import AgentRepository
from agents.health.agent import HealthAgent
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

    if file:
        document = await storage_service.save_file(file, user_id)
        return document.to_dict()

    if note:
        document = create_note_document(note, user_id)
        await repo.insert_report(document)
        return document.to_dict()

    raise HTTPException(status_code=400, detail="No file or note provided")


@router.get("/reports", response_model=list[MedicalDocumentResponse])
async def get_medical_reports(
    user=Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    user_id = user["user_id"]
    reports = await storage_service.get_user_reports(user_id)
    return [MedicalDocumentResponse(**report) for report in reports]


@router.post("/analyze", response_model=MedicalDocumentResponse)
async def analyze_medical_input(
    file: UploadFile = File(None),
    note: str = Form(None),
    user=Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
    repo: MedicalRepository = Depends(get_medical_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
    rag_service = Depends(get_rag_service)
):
    user_id = user["user_id"]
    agent = HealthAgent(repo, agent_repo, rag_service)

    if not file and not note:
        raise HTTPException(status_code=400, detail="Provide a file or a medical note for analysis")

    if file:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            file.file.seek(0)
            document = await storage_service.save_file(file, user_id)
            analysis = await agent.analyze_pdf(tmp_path, user_id, document.file_id)
        finally:
            os.remove(tmp_path)

    else:
        document = create_note_document(note, user_id)
        await repo.insert_report(document)
        analysis = await agent.analyze_text(note, user_id, document.file_id)

    document.analysis = analysis
    document.status = "analyzed"
    return document.to_dict()


@router.get("/dashboard")
async def health_dashboard(
    user=Depends(get_current_user),
    repo: MedicalRepository = Depends(get_medical_repo)
):
    user_id = user["user_id"]
    reports = await repo.get_user_reports(user_id)
    total_reports = len(reports)
    analyzed_reports = [r for r in reports if r.get("analysis")]
    anomaly_count = sum(
        len(r["analysis"].get("anomalies", []))
        for r in analyzed_reports
        if isinstance(r["analysis"], dict)
    )
    latest_report = max(reports, key=lambda r: r.get("upload_time"), default=None)
    recent_insights = []
    for report in analyzed_reports[-3:]:
        if isinstance(report["analysis"], dict):
            insights = report["analysis"].get("insights")
            if insights:
                recent_insights.extend(insights if isinstance(insights, list) else [insights])

    return {
        "total_reports": total_reports,
        "analyzed_reports": len(analyzed_reports),
        "anomaly_count": anomaly_count,
        "latest_report": latest_report,
        "recent_insights": recent_insights[-5:]
    }
