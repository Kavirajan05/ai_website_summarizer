from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.request_model import SummarizeRequest
from app.services.scraper import scrape_website
from app.services.ai_processor import process_with_ai
from app.services.email_service import send_summary_email
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
async def summarize_website(request: SummarizeRequest, background_tasks: BackgroundTasks):
    # Validate the URL internally
    url_str = str(request.url)
    
    # Send process to background queue
    background_tasks.add_task(background_process_and_email, url_str, request.email)
    
    return {
        "status": "processing",
        "message": "Report will be sent to email"
    }
