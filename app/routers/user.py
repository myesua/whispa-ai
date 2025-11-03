from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
# from fastapi import Query
from app.services.supabase_client import supabase

router = APIRouter()

@router.get(
    "/",
    summary="Validate the current user's token/session.",
    status_code=status.HTTP_200_OK
)
async def check_token_status(
    user: dict = Depends(get_current_user) 
):
    """
    Checks if the Bearer token passed in the Authorization header is valid.
    """
    # user_id: str = Query(..., description="User ID to fetch from Supabase")
    response = supabase.table("profiles").select("*").eq("id", user["id"]).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_info = response.data
    return {"access_token": user["access_token"], "full_name": user_info["full_name"], "privacy_mode": user_info["privacy_mode"]}
