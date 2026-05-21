from core.rag.knowledge_base import KnowledgeBase
from database.mongo.repositories.agent_repo import AgentRepository
from database.mongo.repositories.medical_repo import MedicalRepository
from agents.health.agent import HealthAgent


class AgentManager:
    def __init__(self):
        self.rag_service = KnowledgeBase()
        self.rag_service.initialize()
        self.medical_repo = MedicalRepository()
        self.agent_repo = AgentRepository()
        self.health_agent = HealthAgent(
            medical_repo=self.medical_repo,
            agent_repo=self.agent_repo,
            rag_service=self.rag_service
        )

    def get_health_agent(self) -> HealthAgent:
        return self.health_agent
