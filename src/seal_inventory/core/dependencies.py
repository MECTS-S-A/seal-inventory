from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
import os

security = HTTPBearer()


def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"],
        )

        return {
            "username": payload["sub"],
            "owner_token": payload["owner_token"],
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )