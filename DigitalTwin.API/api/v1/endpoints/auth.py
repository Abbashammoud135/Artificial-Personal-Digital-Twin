from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_auth_service, get_current_user
from schemas.auth import RegisterRequest, LoginRequest
import traceback

router = APIRouter()

@router.post("/register")
def register(req: RegisterRequest, auth_service=Depends(get_auth_service)):
    try:
        print("🔵 Registering user:", req.email)
        return auth_service.register(req.full_name, req.email, req.password)
    except Exception as e:
        print(f"❌ Register Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(req: LoginRequest, auth_service=Depends(get_auth_service)):
    try:
        token = auth_service.login(req.email, req.password)
        return {"access_token": token}
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/fullname")
def get_user_fullname(user=Depends(get_current_user),auth_service=Depends(get_auth_service)):
    return auth_service.get_user_fullname(user["user_id"])
   

# use the role based using 
# @router.get("/summary")
# def health_summary(user=Depends(require_role(1))):
#     return {"message": "Health data", "user": user}