import json
import logging
import google.generativeai as genai
from typing import List, Dict
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def rank_videos_with_ai(topic: str, videos: List[Dict]) -> List[Dict]:
    """
    Uses Gemini to rank and explain a list of YouTube videos based on the topic.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    if not videos:
        return []

    video_json = json.dumps(videos, indent=2)
    prompt = f"""
    Analyze the following YouTube videos for the topic: "{topic}".
    
    Tasks:
    1. Rank ALL videos from best to least relevant (1 being best).
    2. For each video, provide a brief explanation of why it is useful for learning about "{topic}".
    
    You MUST output ONLY a valid JSON array of objects, with this structure:
    [
      {{
        "rank": 1,
        "title": "...",
        "channel": "...",
        "videoId": "...",
        "url": "...",
        "explanation": "..."
      }}
    ]
    
    Videos Data:
    {video_json}
    """

    try:
        # Auto-discover models
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        model_name = "gemini-1.5-flash" # Default
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        text_resp = response.text.strip()
        
        # Clean Markdown if needed
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[-1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[-1].split("```")[0].strip()
            
        return json.loads(text_resp)
        
    except Exception as e:
        logger.error(f"YouTube AI Ranking failed: {str(e)}")
        # Return original videos with fallback explanation
        return [
            {**v, "rank": i+1, "explanation": "AI ranking failed, displaying based on search order."}
            for i, v in enumerate(videos)
        ]
