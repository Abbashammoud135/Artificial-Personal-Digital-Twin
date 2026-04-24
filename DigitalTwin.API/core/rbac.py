from fastapi import Depends, HTTPException
from core.dependencies import get_current_user

def require_role(role_id: int):

    def wrapper(user=Depends(get_current_user)):

        if user["role_id"] != role_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        return user

    return wrapper