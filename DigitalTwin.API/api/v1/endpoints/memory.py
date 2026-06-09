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
        request.query,
        user_id=current_user["user_id"]
    )

    return result


class MemoryExecuteRequest(BaseModel):
    action: str
    task: dict

@router.post("/memory/execute")
async def execute_memory(
    request: MemoryExecuteRequest,
    current_user=Depends(get_current_user)
):
    """
    Execute a task action on the Memory Agent.
    Input payload:
    {
      "action": "query",
      "task": {
        "query": "last value of triglycerides - serum test"
      }
    }
    """
    memory_agent = MemoryAgent()

    # Inject current user ID into task dictionary
    task_payload = request.task.copy()
    task_payload["user_id"] = current_user["user_id"]

    result = await memory_agent.execute(
        action=request.action,
        task=task_payload
    )

    return result



