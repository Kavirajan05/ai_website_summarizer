from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.request_model import SummarizeRequest
from app.services.scraper import scrape_website
from app.services.ai_processor import process_with_ai
from app.services.email_service import send_summary_email
from app.services.youtube_service import fetch_youtube_transcript
from app.services.utils import get_logger

router = APIRouter()
logger = get_logger(__name__)

def background_process_and_email(url: str, email: str):
    try:
        logger.info(f"Starting processing for URL: {url}")
        
        # Step 1: Scrape
        scraped_text = scrape_website(url)
        logger.info(f"Successfully scraped {len(scraped_text)} characters.")
        
        # Step 2: AI Process
        report_data = process_with_ai(scraped_text)
        logger.info("Successfully generated AI summary.")
        
        # Step 3: Send Email
        send_summary_email(email, url, report_data)
        logger.info(f"Successfully sent report to {email}.")
        
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")

@router.post("/summarize-website")
async def summarize_website(request: SummarizeRequest):
    url_str = str(request.url)
    try:
        logger.info(f"Starting processing for URL: {url_str}")
        
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
        logger.error(f"Error processing {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize-youtube")
async def summarize_youtube(request: SummarizeRequest):
    url_str = str(request.url)
    try:
        logger.info(f"Starting YouTube processing for URL: {url_str}")
        
        # Step 1: Fetch Transcript
        transcript_text = fetch_youtube_transcript(url_str)
        
        # Step 2: AI Process (same processor works with any text)
        report_data = process_with_ai(transcript_text)
        logger.info("Successfully generated YouTube AI summary.")
        
        return {
            "status": "success",
            "data": report_data
        }
        
    except Exception as e:
        logger.error(f"Error processing YouTube URL {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
