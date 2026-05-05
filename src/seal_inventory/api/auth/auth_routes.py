from fastapi import APIRouter, HTTPException
from seal_inventory.services.auth_service import AuthService
from seal_inventory.schemas.auth import LoginRequest, LoginResponse
from seal_inventory.core.security import create_access_token
from seal_inventory.core.dependencies import get_current_user
from seal_inventory.schemas.auth import MeResponse
from fastapi import Depends

auth_router  = APIRouter(prefix="/api/v1/auth", tags=["auth"])
auth_service = AuthService()

@auth_router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    if not auth_service.authenticate(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": data.username
    }


@auth_router.get("/me", response_model=MeResponse)
def get_me(user=Depends(get_current_user)):
    return {"username": user}