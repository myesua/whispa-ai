from fastapi import APIRouter, HTTPException, Request
from app.services.enquiry_services import EnquiryService

router = APIRouter()

@router.post('/', summary="Create an enquiry")
async def create_enquiry(request: Request):
    try:
        req = await request.json()
        # Validate required fields
        required_fields = ["full_name", "email", "message"]
        for field in required_fields:
            if field not in req:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        enquiry_services = EnquiryService()
        await enquiry_services.create_enquiry(enquiry=req)
        return {"message": "Enquiry created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




