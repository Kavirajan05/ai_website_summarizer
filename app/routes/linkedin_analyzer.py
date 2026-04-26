from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from app.services.linkedin_service import analyze_linkedin_profile

router = APIRouter()
logger = logging.getLogger(__name__)

class LinkedInRequest(BaseModel):
    url: str

@router.post("/analyze-linkedin", status_code=status.HTTP_200_OK)
async def analyze_linkedin_endpoint(request: LinkedInRequest):
    """
    Scrapes a LinkedIn profile using Selenium and analyzes it using Gemini.
    """
    if not request.url.strip() or "linkedin.com/in/" not in request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid LinkedIn profile URL is required."
        )
    
    try:
        logger.info(f"Received LinkedIn analysis request for: {request.url}")
        result = await analyze_linkedin_profile(request.url)
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
