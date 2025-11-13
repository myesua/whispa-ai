from fastapi import HTTPException
from app.services.supabase_client import supabase


class WaitlistService:
    def __init__(self):
        self.supabase = supabase
        self.table_name = 'waitlist'

    async def add_to_waitlist(self, email: str):
        try:
            res = self.supabase.table(self.table_name).insert({"email": email}).execute()
            if not res.data:
                raise HTTPException(status_code=500, detail="Failed to add to waitlist!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))