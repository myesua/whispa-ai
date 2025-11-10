from datetime import date
from fastapi import HTTPException
from app.services.supabase_client import supabase
from prometheus_client import Counter 

DAILY_NOTE_LIMIT = 15

NOTES_GENERATED_TOTAL = Counter(
    'whispa_notes_generated_total', 'Total QA notes generated',
    ['user_id', 'day']
)

class UsageService:
    def __init__(self):
        self.supabase = supabase

    async def check_and_increment_note_count(self, user_id: str):
        today_str = date.today().isoformat()
        
        try:
            response = self.supabase.table("user_usage").select("notes_count").eq("user_id", user_id).eq("day", today_str).single().execute()
            record_data = getattr(response, 'data', None)
            current_count = record_data['notes_count'] if record_data else 0

        except Exception as e:
            if "No rows returned" in str(e) or "zero rows" in str(e).lower():
                current_count = 0
            else:
                raise HTTPException(status_code=500, detail=f"Database error during usage check: {str(e)}")

        if current_count >= DAILY_NOTE_LIMIT:
            raise HTTPException(
                status_code=429, # 429 Too Many Requests
                detail=f"Daily limit of {DAILY_NOTE_LIMIT} QA notes exceeded. Please wait 24 hours or upgrade to a paid plan."
            )
            
        new_count = current_count + 1
        payload = {
            "user_id": user_id,
            "day": today_str,
            "notes_count": new_count
        }
        try:
            self.supabase.table("user_usage").upsert(payload, on_conflict="user_id,day").execute()
            NOTES_GENERATED_TOTAL.labels(user_id=user_id, day=today_str).inc()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error during usage update: {str(e)}")

        return True 