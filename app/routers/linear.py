from fastapi import APIRouter, HTTPException, Request
from app.services.linear_service import LinearService

router = APIRouter()

@router.post('/create-issue', summary="Creates issue on Linear")
async def create_issue(request: Request):
    try:
        request_data = await request.json()
        linear_service = LinearService()
        response = linear_service.create_issue(title=request_data["title"], description=request_data["description"] or '', team_id=request_data["team_id"], priority=request_data["priority"] or 1, label_ids=request_data.get("label_ids") or [])

        return {"success": True, "issue": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
