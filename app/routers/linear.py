from fastapi import APIRouter, HTTPException, Request
from app.services.linear_service import LinearService

router = APIRouter()

@router.post('/create-issue', summary="Creates issue on Linear")
async def create_issue(request: Request):
    try:
        request_data = await request.json()
        # Validate required fields
        required_fields = ["title", "description", "team_id", "linear_api_key", "image"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        linear_service = LinearService()
        response = linear_service.create_issue(title=request_data["title"], description=request_data["description"] or "", team_id=request_data["team_id"], priority=request_data["priority"] or 1, label_ids=request_data["label_ids"] or [], linear_api_key=request_data['linear_api_key'], image_base64=request_data["image"] or None)

        return {"success": True, "issue": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
