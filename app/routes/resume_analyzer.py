from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.resume_extraction import extract_resume_text
from app.services.resume_ai_analyzer import analyze_resume_with_ai
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyze-resume", status_code=status.HTTP_200_OK)
async def analyze_resume_endpoint(
    file: UploadFile = File(...)
):
    """
    Upload a resume (PDF or DOCX), extract text, analyze with Gemini AI,
    and return the structured analysis directly in the response.
    No email required.
    """
    # 1. Validate file type
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported."
        )

    try:
        logger.info(f"Received resume analysis request for: {file.filename}")

        # 2. Read & validate size
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty."
            )
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum allowed size is 5MB."
            )

        # 3. Extract text
        resume_text = extract_resume_text(content, file.filename)
        if not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any text from the file. It may be image-based or corrupted."
            )

        # 4. AI Analysis (returns dict directly)
        analysis = await analyze_resume_with_ai(resume_text)

        return {
            "message": "Resume analyzed successfully",
            "data": analysis
        }

    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error in resume analyzer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
