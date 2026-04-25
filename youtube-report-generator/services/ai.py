import os
import httpx
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

async def rank_videos(videos: List[Dict]) -> List[Dict]:
    """
    Uses an LLM to rank and explain a list of YouTube videos based on the topic.
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        logger.error("LLM_API_KEY not found in environment variables.")
        return []

    # Prepare prompt
    video_json = json.dumps(videos, indent=2)
    prompt = f"""You are given REAL YouTube video data.

STRICT RULES:
* Rank ALL videos
* Do NOT skip any
* Do NOT hallucinate
* Do NOT change titles or links
* Output ONLY valid JSON array of objects

For EACH video return an object with:
* "rank" (integer, 1 being best)
* "title" (string)
* "channel" (string)
* "videoId" (string)
* "url" (string)
* "explanation" (string)

Videos Data:
{video_json}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile", # Using an active Groq model
        "messages": [
            {"role": "system", "content": "You are a helpful API that returns strictly valid JSON arrays based on the prompt instructions. Do not wrap in ```json markup, just return the raw JSON array."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            import re
            # Extract JSON array using regex. This handles any surrounding text.
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                ai_analysis = json.loads(json_str)
                return ai_analysis
            else:
                logger.error(f"Failed to find JSON array in response: {content}")
                return []
            
    except Exception as e:
        logger.error(f"Error querying AI API: {e}")
        return []
