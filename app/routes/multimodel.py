from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from app.services.multimodel_service import run_multimodel_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

class MultimodelRequest(BaseModel):
    query: str

@router.post("/multimodel-summarize", status_code=status.HTTP_200_OK)
async def multimodel_summarize_endpoint(request: MultimodelRequest):
    """
    Runs multi-model summarization querying OpenRouter, Groq, and Gemini.
    Returns the aggregated and summarized JSON result.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty"
        )
    
    try:
        logger.info(f"Received multimodel summarization request: {request.query[:50]}...")
        result = await run_multimodel_pipeline(request.query)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Multimodel summarizer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during multi-model processing: {str(e)}"
        )
