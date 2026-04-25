import os
import httpx
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

async def search_youtube(topic: str) -> List[str]:
    """
    Searches YouTube for videos on the given topic and returns a list of video IDs.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("YOUTUBE_API_KEY not found in environment variables.")
        return []

    url = f"{YOUTUBE_API_URL}/search"
    params = {
        "key": api_key,
        "q": topic,
        "type": "video",
        "maxResults": 4,
        "part": "snippet"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"YouTube Search API error: {response.text}")
            return []
            
        data = response.json()
        video_ids = [item["id"]["videoId"] for item in data.get("items", []) if "videoId" in item["id"]]
        return video_ids

async def get_video_details(video_ids: List[str]) -> List[Dict]:
    """
    Fetches details for the provided video IDs.
    """
    if not video_ids:
        return []

    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"{YOUTUBE_API_URL}/videos"
    params = {
        "key": api_key,
        "id": ",".join(video_ids),
        "part": "snippet,contentDetails,status"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"YouTube Videos API error: {response.text}")
            return []
            
        data = response.json()
        videos = []
        for item in data.get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "videoId": item["id"],
                "url": f"https://www.youtube.com/watch?v={item['id']}"
            })
            
        return videos
