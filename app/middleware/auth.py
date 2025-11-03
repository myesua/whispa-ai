from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.supabase_client import supabase

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        resp = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = getattr(resp, "user", None)
    error = getattr(resp, "error", None)

    if error or not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"id": user.id, "email": user.email, "access_token": token}
