from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
from dotenv import load_dotenv

import services.youtube as youtube
import services.ai as ai
import services.email as email_service
from utils.formatter import format_report

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Learning Report Generator")

# Models for request/response validation
class ReportRequest(BaseModel):
    topic: str
    email: EmailStr
    send_email: bool = False

class VideoData(BaseModel):
    title: str
    channel: str
    videoId: str
    url: str

class AIAnalysis(BaseModel):
    rank: int
    title: str
    channel: Optional[str] = None
    videoId: str
    url: str
    explanation: str

class ReportResponse(BaseModel):
    status: str
    topic: str
    videos: List[VideoData]
    ai_analysis: List[AIAnalysis]
    final_report: str
    email_sent: bool

@app.post("/youtube-report", response_model=ReportResponse)
async def generate_youtube_report(request: ReportRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received request for topic: {request.topic}")

    # Step 1: Fetch Video IDs
    try:
        video_ids = await youtube.search_youtube(request.topic)
    except Exception as e:
        logger.error(f"Failed searching YouTube: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch initial video search")

    if not video_ids:
        raise HTTPException(status_code=404, detail=f"No videos found for topic: {request.topic}")

    # Step 2: Fetch Video Details
    try:
        videos = await youtube.get_video_details(video_ids)
    except Exception as e:
        logger.error(f"Failed getting YouTube details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video details")

    if not videos:
        raise HTTPException(status_code=404, detail="Could not retrieve details for videos")

    # Step 3: AI Ranking & Explanation
    try:
        ai_analysis_data = await ai.rank_videos(videos)
    except Exception as e:
        logger.error(f"AI ranking failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform AI ranking")

    if not ai_analysis_data:
        raise HTTPException(status_code=500, detail="AI analysis returned no valid results")

    # Step 4: Generate Final Report
    # Format AI output nicely for text
    formatted_ai_text = "\n\n".join([f"{idx+1}. {item.get('title')} ({item.get('url')})\nExplanation: {item.get('explanation')}" for idx, item in enumerate(ai_analysis_data)])
    final_report = format_report(request.topic, formatted_ai_text)
    
    email_sent_status = False

    # Step 5: Email Optional
    if request.send_email and request.email:
        logger.info(f"Scheduling email to {request.email} in background")
        background_tasks.add_task(email_service.send_report_email, request.email, request.topic, final_report)
        email_sent_status = True  # It represents intention since it's queued

    return ReportResponse(
        status="success",
        topic=request.topic,
        videos=videos,
        ai_analysis=ai_analysis_data,
        final_report=final_report,
        email_sent=email_sent_status
    )
