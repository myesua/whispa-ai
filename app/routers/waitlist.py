from fastapi import APIRouter, Request, HTTPException
from app.services.waitlist_service import WaitlistService

router = APIRouter()

@router.post('/', summary="Add email to waitlist")
async def add_to_waitlist(request: Request):
    try:
        req = await request.json()
        email = req.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        waitlist_service = WaitlistService()
        await waitlist_service.add_to_waitlist(email)
        
        return {"success": True, "message": "Email added to waitlist"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))