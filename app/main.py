from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, notes, audio, linear, user, attachments, enquiry, waitlist
from .middleware.auth import get_current_user
from dotenv import load_dotenv
from .dependencies import get_whisper_model 
import logging
from app.middleware.prometheus import PrometheusMiddleware, metrics_endpoint
from app.services.clean_up_queue import cleanup_worker
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI()

try:
    get_whisper_model()
    logging.info("Faster-Whisper model loading complete. System ready for transcription requests.")
except Exception as e:
    logging.error(f"CRITICAL ERROR: Failed to load Faster-Whisper model at startup: {e}")

app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/metrics", metrics_endpoint)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_worker())
    logging.info("Background cleanup worker task scheduled.")

app.include_router(auth.router)
# Protect other routes with authentication
app.include_router(notes.router, prefix="/v1/notes", tags=["notes"], dependencies=[Depends(get_current_user)])
# app.include_router(ocr.router, prefix="/v1/ocr", tags=["ocr"], dependencies=[Depends(get_current_user)])
app.include_router(audio.router, prefix="/v1/audio", tags=["audio"], dependencies=[Depends(get_current_user)])
app.include_router(linear.router, prefix="/v1/linear", tags=["linear"], dependencies=[Depends(get_current_user)])
app.include_router(user.router, prefix="/v1/user", tags=["user"], dependencies=[Depends(get_current_user)])
app.include_router(attachments.router, prefix="/v1/attachments", tags=["attachments"])
app.include_router(enquiry.router, prefix="/v1/enquiry", tags=["enquiry"])
app.include_router(waitlist.router, prefix="/v1/waitlist", tags=["waitlist"])

@app.get("/")
async def root():   
    return {"message": "Welcome to the Whispa AI QA Agent!"}


# @app.post("/", tags=["OCR"])
# async def root_post(request: Request):
#     """Accept POST / as shorthand for OCR processing (used by tests)."""
#     # Delegate to OCR router's process_ocr by calling its endpoint function indirectly
#     from app.routers.ocr import process_ocr
#     return await process_ocr(request)

