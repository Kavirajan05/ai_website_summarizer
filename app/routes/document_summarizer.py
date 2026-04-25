from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.pdf_service import extract_text_from_pdf
from app.services.doc_ai_processor import summarize_document_with_ai
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/summarize-document", status_code=status.HTTP_200_OK)
async def summarize_document_endpoint(
    file: UploadFile = File(...)
):
    """
    Accepts a PDF file, extracts text, summarizes it using Gemini, and returns the results.
    """
    # 1. Validate File Type
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported."
        )

    try:
        logger.info(f"Received document summarization request for file {file.filename}")
        
        # 2. Read File Content
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty."
            )

        # 3. Extract Text
        text = await extract_text_from_pdf(content)
        
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any text from the PDF. It might be image-based or protected."
            )

        # 4. Summarize Text with Gemini
        ai_data = await summarize_document_with_ai(text)
        
        return {
            "message": "Document summarized successfully",
            "data": ai_data
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in document summarizer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {str(e)}"
        )
