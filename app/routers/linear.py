from fastapi import APIRouter, HTTPException, Request
from app.services.linear_service import LinearService

router = APIRouter()

@router.post('/create-issue', summary="Creates issue on Linear")
async def create_issue(request: Request):
    try:
        request_data = await request.json()
        # Validate required fields
        required_fields = ["title", "description", "team_id", "api_key", "images"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        linear_service = LinearService()
        response = await linear_service.create_issue(title=request_data["title"], description=request_data["description"] or "", team_id=request_data["team_id"], priority=request_data["priority"] or 1, label_ids=request_data["label_ids"] or [], api_key=request_data['api_key'], image_base64_list=request_data["images"] or [])

        return {"success": True, "issue": response.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
