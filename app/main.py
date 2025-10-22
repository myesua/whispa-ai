from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, notes, ocr, audio, linear
from .middleware.auth import get_current_user
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
# Protect other routes with authentication
app.include_router(notes.router, dependencies=[Depends(get_current_user)])
app.include_router(ocr.router, dependencies=[Depends(get_current_user)])
app.include_router(audio.router, dependencies=[Depends(get_current_user)])
app.include_router(linear.router, prefix="/linear", tags=["linear"], dependencies=[Depends(get_current_user)])

@app.get("/")
async def root():
    return {"message": "Welcome to the Whispa AI Notes App!"}


@app.post("/", tags=["OCR"])
async def root_post(request: Request):
    """Accept POST / as shorthand for OCR processing (used by tests)."""
    # Delegate to OCR router's process_ocr by calling its endpoint function indirectly
    from app.routers.ocr import process_ocr
    return await process_ocr(request)

