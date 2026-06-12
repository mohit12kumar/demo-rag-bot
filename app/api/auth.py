from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.mysql import SessionLocal
from app.database.models import User

from app.auth.password import (
    hash_password,
    verify_password
)

from app.auth.jwt_handler import (
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# Schemas
# ==========================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==========================================
# Register User
# ==========================================

@router.post("/register")
def register(request: RegisterRequest):

    db: Session = SessionLocal()

    try:

        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        user = User(
            name=request.name,
            email=request.email,
            password=hash_password(
                request.password
            )
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# ==========================================
# Login User
# ==========================================

@router.post("/login")
def login(request: LoginRequest):

    db: Session = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not verify_password(
            request.password,
            user.password
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email
            }
        )

        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    finally:

        db.close()


# ==========================================
# User Profile
# ==========================================

@router.get("/profile/{user_id}")
def get_profile(user_id: int):

    db: Session = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at
            }
        }

    finally:

        db.close()