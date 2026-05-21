from fastapi import APIRouter, Depends
from schemas.health.health_profile import (
    HealthProfileCreate,
    HealthProfileUpdate,
    HealthProfileResponse
)
from core.dependencies import get_current_user, get_health_profile_service

router = APIRouter()


@router.get("/", response_model=HealthProfileResponse)
async def get_profile(
    user=Depends(get_current_user),
    service=Depends(get_health_profile_service)
):
    return service.get_profile(user["user_id"])


@router.post("/", response_model=HealthProfileResponse)
async def create_profile(
    data: HealthProfileCreate,
    user=Depends(get_current_user),
    service=Depends(get_health_profile_service)
):
    return service.create_profile(user["user_id"], data)


@router.put("/", response_model=HealthProfileResponse)
async def update_profile(
    data: HealthProfileUpdate,
    user=Depends(get_current_user),
    service=Depends(get_health_profile_service)
):
    return service.update_profile(user["user_id"], data)