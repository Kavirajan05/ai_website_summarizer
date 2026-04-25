from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from app.services.analyzer import analyzer_service
from app.schemas.resume import AnalysisResponse
from pydantic import EmailStr

router = APIRouter()

@router.post("/upload-resume", response_model=AnalysisResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a resume (PDF/DOCX) and analyze it. 
    The results will be sent to the provided email.
    """
    # 1. Basic Validation
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    
    # Check file size (e.g., limit to 5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    # 2. Process in Background
    # We pass the content because the file object will be closed after the request returns
    background_tasks.add_task(
        analyzer_service.process_and_notify,
        content,
        file.filename,
        email
    )

    return AnalysisResponse()
