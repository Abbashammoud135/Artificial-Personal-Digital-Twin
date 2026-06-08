from fastapi import APIRouter, Depends

from agents.memory.agent import MemoryAgent
from core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

class MemoryQueryRequest(BaseModel):
    query: str
    
@router.post("/memory/query")
async def query_memory(
    request: MemoryQueryRequest,
    current_user=Depends(get_current_user)
):
    """
    {
        "query": "high cardiovascular risk patients"
    }
    """

    memory_agent = MemoryAgent()

    result = await memory_agent.query_memory(
        request.query
    )

    return result


