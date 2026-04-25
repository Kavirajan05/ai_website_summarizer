from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.resume_ai_service import extract_text_from_resume, analyze_resume_with_ai
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyze-resume", status_code=status.HTTP_200_OK)
async def analyze_resume_endpoint(
    file: UploadFile = File(...)
):
    """
    Accepts a PDF or DOCX resume, analyzes it with Gemini AI,
    and returns structured results directly to the frontend.
    No email is required.
    """
    # 1. Validate file type
    allowed_extensions = (".pdf", ".docx")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX resume files are supported."
        )

    try:
        logger.info(f"Received resume analysis request for: {file.filename}")

        # 2. Read and validate file size
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty."
            )
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB."
            )

        # 3. Extract text
        resume_text = extract_text_from_resume(content, file.filename)
        if not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the resume. It may be image-based or password-protected."
            )

        # 4. Analyze with Gemini
        analysis = await analyze_resume_with_ai(resume_text)

        return {
            "message": "Resume analyzed successfully",
            "data": analysis
        }

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error in resume analyzer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )
