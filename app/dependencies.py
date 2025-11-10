# app/dependencies.py
from app.services.usage_service import UsageService

def get_usage_service() -> UsageService:
    """Dependency to provide the UsageService instance."""
    return UsageService()