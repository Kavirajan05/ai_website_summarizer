from fastapi import APIRouter, BackgroundTasks, HTTPException
from schemas.request import SummarizeRequest
from services.youtube import extract_video_id, fetch_transcript
from services.summarizer import generate_summary
from services.email import send_email
from utils.helpers import get_logger, format_error

router = APIRouter()
logger = get_logger()

def process_summarization(email: str, youtube_url: str):
    """
    Background worker that handles the full summarization flow.
    """
    try:
        logger.info(f"Processing summarization for: {youtube_url}")

        # 1. Extract Video ID
        video_id = extract_video_id(youtube_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {youtube_url}")

        # 2. Fetch Transcript
        transcript = fetch_transcript(video_id)

        # 3. Generate Summary
        summary = generate_summary(transcript)

        # 4. Send Email
        subject = "Your YouTube Video Summary"
        send_email(email, subject, summary)

        logger.info(f"Summary successfully sent to {email}")

    except Exception as e:
        error_msg = format_error(e)
        logger.error(error_msg)
        # In production, we might want to alert the user or log this elsewhere.
        # Since this is a background task, we don't return an error response.

@router.post("/summarize")
async def summarize_video(request: SummarizeRequest, background_tasks: BackgroundTasks):
    """
    Endpoint that accepts a YouTube URL and email, and starts the summarization process.
    """
    # Simply trigger the background task and return immediately
    background_tasks.add_task(process_summarization, str(request.email), str(request.youtube_url))
    return {"message": "Processing started"}
