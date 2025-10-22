from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    privacy_mode: bool = True

@router.post("/register")
async def register(payload: RegisterPayload):
    try:
        resp = supabase.auth.sign_up({
            "email": payload.email.strip(),
            "password": payload.password
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = getattr(resp, "user", None)
    error = getattr(resp, "error", None)

    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not user or not getattr(user, "id", None):
        raise HTTPException(status_code=500, detail="Could not create user")

    profile_payload = {
        "id": user.id, 
        "email": payload.email,
        "full_name": payload.full_name,
        "privacy_mode": payload.privacy_mode
    }

    # update profile
    supabase.table("profiles").upsert(profile_payload).execute()

    return {
        "id": user.id,
        "email": payload.email,
        "full_name": payload.full_name,
        "privacy_mode": payload.privacy_mode
    }

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(payload: LoginPayload):
    try:
        resp = supabase.auth.sign_in_with_password({
            "email": payload.email.strip(),
            "password": payload.password
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = getattr(resp, "user", None)
    session = getattr(resp, "session", None)
    error = getattr(resp, "error", None)

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = getattr(session, "access_token", None) if session else None

    profile_resp = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
    profile_data = getattr(profile_resp, "data", None) or {}

    return {
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
        "full_name": profile_data.get("full_name", "")
    }