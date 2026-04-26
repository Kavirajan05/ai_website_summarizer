from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.ad_generator_service import generate_marketing_image
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate-ad")
async def generate_ad(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        # Generate enhanced image
        base64_image = generate_marketing_image(image_bytes, title, description)
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{base64_image}",
            "title": title
        }
    except Exception as e:
        logger.error(f"Ad generation route failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
