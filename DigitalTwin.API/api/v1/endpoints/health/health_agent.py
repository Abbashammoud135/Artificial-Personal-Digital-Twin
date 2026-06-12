from pydantic import BaseModel
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.storage_service import StorageService
from database.mongo.repositories.medical_repo import MedicalRepository
from database.mongo.repositories.agent_repo import AgentRepository
from agents.health.agent import HealthAgent
from core.dependencies import get_auth_service, get_current_user, get_storage_service, get_medical_repo, get_agent_repo, get_rag_service
from utils.helpers import create_note_document_helper as create_note_document
import os
import tempfile
from core.llm.groq_llama_client import get_llm
from agents.memory.agent import MemoryAgent

router = APIRouter()


class HealthAgentQuestion(BaseModel):
    question: str


@router.post("/ask")
async def ask_health_agent(
    data: HealthAgentQuestion,
    user=Depends(get_current_user),
    repo: MedicalRepository = Depends(get_medical_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
    auth_service = Depends(get_auth_service),
    rag_service = Depends(get_rag_service)
):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    memory = MemoryAgent()
    agent = HealthAgent(repo, agent_repo, rag_service)
    userFullName=auth_service.get_user_fullname(user["user_id"])
    doIneedToUseMemory = await agent.doINeedToUseMemory(question,user["user_id"])
    print(f"Health Agent determined memory usage: {doIneedToUseMemory.get('need_memory')} with query {doIneedToUseMemory.get('query')}")
    if doIneedToUseMemory.get('need_memory'):
        memory = await memory.query_memory(doIneedToUseMemory.get('query'), user["user_id"])
        print(f"Memory Agent returned : {memory['answer']}")
    response = await agent.ask_question(memory.get('answer') if doIneedToUseMemory.get('need_memory') else "",question,userFullName,user["user_id"])
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


class AnalysisInput(BaseModel):
    summary: str
    recommendations: List[str]
    insights: List[str]
    raw_output: str
    question: str
    chat_history: List[dict] = []
    
def build_prompt(payload: AnalysisInput):
    return f"""
You are a medical AI assistant.

You must answer the user's question using ONLY the provided medical context.

### MEDICAL CONTEXT

SUMMARY:
{payload.summary}

RECOMMENDATIONS:
{chr(10).join(payload.recommendations)}

INSIGHTS:
{chr(10).join(payload.insights)}

RAW DATA:
{payload.raw_output}

CHAT HISTORY
{payload.chat_history}
---

### USER QUESTION
{payload.question}
---

### RULES
- Use the given medical context
- Be clear, helpful, and medically safe
- use chathistory to maintain context but do not reference it explicitly in your answer, especilly on using 'this','before','previously' and similar terms
- the most important thing to answer the question accurately and be direct to the point
- When listing items, always use bullet points or numbered lists (1, 2, 3) for clarity.
- if you don't know the answer, say you don't know. Do not try to make up
- Do not use markdown formatting such as **bold**, *italics*, or other asterisks. Use plain text only.
Start answering immediately.
"""

@router.post("/analyze/stream")
async def analyze_stream(payload: AnalysisInput):

    prompt = build_prompt(payload)
    llm = get_llm()
    print(f"------Start of payload Generated prompt for LLM:\n{payload}\n--- End of payload ---")

    async def stream():
        async for chunk in llm.astream(prompt):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(stream(), media_type="text/plain")