from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from pydantic import BaseModel
from services.storage_service import StorageService
from database.mongo.repositories.medical_repo import MedicalRepository
from database.mongo.repositories.agent_repo import AgentRepository
from agents.health.agent import HealthAgent
from core.dependencies import get_current_user, get_storage_service, get_medical_repo, get_agent_repo, get_rag_service
from utils.helpers import create_note_document_helper as create_note_document
import os
import tempfile

router = APIRouter()


class HealthAgentQuestion(BaseModel):
    question: str


@router.post("/ask")
async def ask_health_agent(
    data: HealthAgentQuestion,
    user=Depends(get_current_user),
    repo: MedicalRepository = Depends(get_medical_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
    rag_service = Depends(get_rag_service)
):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    agent = HealthAgent(repo, agent_repo, rag_service)
    response = await agent.ask_question(question, user["user_id"])
    return response


@router.post("/analyze")
async def agent_analyze_input(
    file: UploadFile | None = File(None),
    note: str | None = Form(None),
    user=Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service),
    repo: MedicalRepository = Depends(get_medical_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
    rag_service = Depends(get_rag_service)
):
    user_id = user["user_id"]
    agent = HealthAgent(repo, agent_repo, rag_service)

    if file:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            document = await storage_service.save_file(file, user_id)
            analysis = await agent.analyze_pdf(tmp_path, user_id, document.file_id)
        finally:
            os.remove(tmp_path)

        return {
            "file_id": document.file_id,
            "user_id": document.user_id,
            "file_type": document.file_type,
            "file_url": document.file_url,
            "upload_time": document.upload_time,
            "status": "analyzed",
            "analysis": analysis
        }

    if note:
        document = create_note_document(note, user_id)
        await repo.insert_report(document)
        analysis = await agent.analyze_text(note, user_id, document.file_id)
        return {
            "file_id": document.file_id,
            "user_id": document.user_id,
            "file_type": document.file_type,
            "file_url": document.file_url,
            "upload_time": document.upload_time,
            "status": "analyzed",
            "analysis": analysis
        }

    raise HTTPException(status_code=400, detail="Provide a file or note to analyze")
