from datetime import datetime, timedelta
from jose import jwt
import uuid
import os


def create_access_token(
        username: str,
        owner_id: str,
):
    payload = {
        "sub": username,
        "owner_id": owner_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET"),
        algorithm="HS256",
    )