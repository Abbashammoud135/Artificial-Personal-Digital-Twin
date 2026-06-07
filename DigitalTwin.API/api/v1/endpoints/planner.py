"""
Planner Agent Endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.planner.agent import PlannerAgent
from agents.planner.schema import Plan

router = APIRouter(prefix="/planner", tags=["planner"])


class PlanRequest(BaseModel):
    """Request model for planner endpoint."""
    request: str


@router.post("/plan", response_model=Plan)
def create_plan(plan_request: PlanRequest):
    """
    Create a plan from a user request.
    
    The planner breaks down the user's goal into executable tasks.
    
    Example:
        Input: "Analyze my latest blood report"
        Output: A plan with tasks to retrieve and analyze the report
    """
    try:
        planner = PlannerAgent()
        plan = planner.execute(plan_request.request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")
