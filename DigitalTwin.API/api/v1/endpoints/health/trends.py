from fastapi import APIRouter, Depends

from core.dependencies import (
    get_current_user,
    get_trend_service
)

from schemas.health.trend import TrendResponse

router = APIRouter()


@router.get("/", response_model=TrendResponse)
async def get_trends(
    user=Depends(get_current_user),
    service=Depends(get_trend_service)
):

    return await service.get_user_trends(
        user["user_id"]
    )