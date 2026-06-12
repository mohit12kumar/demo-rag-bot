from fastapi import Depends, Header
from fastapi.security import HTTPBearer
from typing import Optional

from app.auth.jwt_handler import (
    verify_token
)

security = HTTPBearer()


def get_current_user(credentials=Depends(security)):

    token = credentials.credentials

    return verify_token(token)


def get_optional_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return {"user_id": 1}
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return {"user_id": 1}
        payload = verify_token(token)
        return payload
    except Exception:
        return {"user_id": 1}