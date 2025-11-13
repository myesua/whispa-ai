


from fastapi import HTTPException
from app.services.supabase_client import supabase


class EnquiryService():
    def __init__(self) -> None:
        self.supabase = supabase
        self.table_name = "enquiries"

    async def create_enquiry(self, enquiry: dict):
        res = self.supabase.table(self.table_name).insert(enquiry).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to create enquiry!")
        print('response_enquiry: ', res.data)
        return res.data