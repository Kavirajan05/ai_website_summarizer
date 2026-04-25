from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
import logging
from app.services.yt_search_service import search_youtube, get_video_details
from app.services.yt_ai_ranker import rank_videos_with_ai
from app.services.yt_report_formatter import format_youtube_report

router = APIRouter()
logger = logging.getLogger(__name__)

class YTReportRequest(BaseModel):
    topic: str

@router.post("/youtube-report", status_code=status.HTTP_200_OK)
async def generate_youtube_report_endpoint(request: YTReportRequest):
    """
    Searches YouTube, ranks videos with AI, and generates a learning report.
    """
    logger.info(f"Received YouTube report request for topic: {request.topic}")

    # 1. Search YouTube
    video_ids = await search_youtube(request.topic)
    if not video_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No videos found for topic: {request.topic}"
        )

    # 2. Get Details
    videos = await get_video_details(video_ids)
    if not videos:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve video details from YouTube."
        )

    # 3. AI Ranking
    ai_analysis = await rank_videos_with_ai(request.topic, videos)
    
    # 4. Format Report
    final_report = format_youtube_report(request.topic, ai_analysis)

    return {
        "status": "success",
        "data": {
            "topic": request.topic,
            "ai_analysis": ai_analysis,
            "final_report": final_report
        }
    }
