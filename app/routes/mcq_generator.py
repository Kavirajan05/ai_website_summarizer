from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.mcq_service import extract_text_from_file, generate_mcqs
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate-mcqs")
async def generate_mcqs_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload a document and generate MCQs.
    No email is sent; results are returned directly to the frontend.
    """
    try:
        logger.info(f"MCQ generation requested for: {file.filename}")
        
        # 1. Read and Extract Text
        content = await file.read()
        text = extract_text_from_file(content, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document contains no readable text.")

        # 2. Generate MCQs using AI
        mcq_data = await generate_mcqs(text)
        
        return {
            "status": "success",
            "data": mcq_data
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"MCQ Endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
