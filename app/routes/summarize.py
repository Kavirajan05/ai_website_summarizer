from fastapi import APIRouter, HTTPException
from app.models.request_model import SummarizeRequest
from app.services.scraper import scrape_website
from app.services.ai_processor import process_with_ai
from app.services.youtube_service import fetch_youtube_transcript
from app.services.utils import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/summarize-website")
async def summarize_website(request: SummarizeRequest):
    url_str = str(request.url)
    try:
        logger.info(f"Starting website processing for URL: {url_str}")
        
        # Step 1: Scrape
        scraped_text = scrape_website(url_str)
        
        # Step 2: AI Process
        report_data = process_with_ai(scraped_text)
        logger.info("Successfully generated AI summary.")
        
        return {
            "status": "success",
            "data": report_data
        }
        
    except Exception as e:
        logger.error(f"Error processing website {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize-youtube")
async def summarize_youtube(request: SummarizeRequest):
    url_str = str(request.url)
    try:
        logger.info(f"Starting YouTube processing for URL: {url_str}")
        
        # Step 1: Fetch Transcript
        transcript_text = fetch_youtube_transcript(url_str)
        
        # Step 2: AI Process
        report_data = process_with_ai(transcript_text)
        logger.info("Successfully generated YouTube AI summary.")
        
        return {
            "status": "success",
            "data": report_data
        }
        
    except Exception as e:
        logger.error(f"Error processing YouTube URL {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
