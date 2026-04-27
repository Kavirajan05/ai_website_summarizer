from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.linkedin_service import analyze_linkedin_profile

router = APIRouter()

class LinkedInRequest(BaseModel):
    url: Optional[str] = None
    profile_text: Optional[str] = None

@router.post("/analyze-linkedin")
async def analyze_linkedin(request: LinkedInRequest):
    try:
        # Check if either URL or profile text is provided
        if not request.url and not request.profile_text:
            raise HTTPException(status_code=400, detail="Either a LinkedIn URL or profile text is required.")
            
        result = await analyze_linkedin_profile(url=request.url, profile_text=request.profile_text)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
