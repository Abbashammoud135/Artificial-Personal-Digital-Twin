from datetime import datetime
from core.pipeline.medical_pipeline import MedicalPipeline
from database.mongo.repositories.medical_repo import MedicalRepository
from database.mongo.repositories.agent_repo import AgentRepository
from core.rag.knowledge_base import KnowledgeBase


class HealthAgent:

    def __init__(self,
                 medical_repo: MedicalRepository,
                 agent_repo: AgentRepository,
                 rag_service: KnowledgeBase | None = None):
        self.medical_repo = medical_repo
        self.agent_repo = agent_repo
        self.rag_service = rag_service or KnowledgeBase()
        self.rag_service.initialize()
        self.pipeline = MedicalPipeline(self.rag_service)

    async def analyze_pdf(self, file_path: str, user_id: str, file_id: str | None = None) -> dict:
        analysis = self.pipeline.process_pdf(file_path)
        if file_id:
            await self.medical_repo.update_report_analysis(file_id, analysis)
        await self._save_reasoning(user_id, "analyze_pdf", file_path, analysis)
        return analysis

    async def analyze_text(self, text: str, user_id: str, file_id: str | None = None) -> dict:
        analysis = self.pipeline.process_text(text)
        if file_id:
            await self.medical_repo.update_report_analysis(file_id, analysis)
        await self._save_reasoning(user_id, "analyze_text", text, analysis)
        return analysis

    async def ask_question(self,memory: str, question: str, user_name: str, user_id: str) -> dict:
        analysis = self.pipeline.process_question(question,user_name,memory)
        await self._save_reasoning(user_id, "ask_question", question, analysis,userName=user_name,memory=memory)
        return analysis
    async def doINeedToUseMemory(self,question: str,user_id: str) -> dict:
        answer = self.pipeline.do_i_need_to_use_memory(question)
        print(f"Raw response for memory usage decision: {answer}")
        return answer
       

    async def _save_reasoning(self, user_id: str, action: str, input_value: str, analysis: dict, userName: str = None, memory: str = None):
        payload = {
            "user_id": user_id,
            "action": action,
            "input": input_value,
            "analysis": analysis,
            "user_name": userName,
            "memory": memory,
            "rag_references": analysis.get("rag_references") if isinstance(analysis, dict) else None,
            "timestamp": datetime.utcnow()
        }
        await self.agent_repo.save_reasoning(payload)
