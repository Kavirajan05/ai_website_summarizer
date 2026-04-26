from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from app.services.linkedin_service import analyze_linkedin_profile

router = APIRouter()
logger = logging.getLogger(__name__)

class LinkedInRequest(BaseModel):
    url: str | None = None
    profile_text: str | None = None

@router.post("/analyze-linkedin", status_code=status.HTTP_200_OK)
async def analyze_linkedin_endpoint(request: LinkedInRequest):
    """
    Analyzes a LinkedIn profile using either a URL (Scraping) or direct text.
    """
    if not request.url and not request.profile_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a LinkedIn URL or profile text is required."
        )
    
    try:
        logger.info(f"Received LinkedIn analysis request. URL: {request.url}, Manual: {bool(request.profile_text)}")
        result = await analyze_linkedin_profile(url=request.url, manual_text=request.profile_text)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"LinkedIn analyzer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the LinkedIn profile: {str(e)}"
        )
