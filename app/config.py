from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    """Simple environment-backed settings object.

    This avoids pinning to pydantic v1/v2 differences during tests. It's
    intentionally minimal and reads common environment variables.
    """
    api_key: str = os.getenv("API_KEY", "")
    ocr_language: str = os.getenv("OCR_LANGUAGE", "eng")
    audio_language: str = os.getenv("AUDIO_LANGUAGE", "en-US")
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage")

    # LLM / Gemini / OpenAI configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_endpoint: str = os.getenv("GEMINI_ENDPOINT", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro-latest")

    # Third-party integration keys (optional)
    notion_api_key: str = os.getenv("NOTION_API_KEY", "")
    linear_api_key: str = os.getenv("LINEAR_API_KEY", "")

    # Privacy: if True, do not persist any user content to disk/database
    privacy_mode: bool = os.getenv("PRIVACY_MODE", "true").lower() in ("1", "true", "yes")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


settings = Settings()