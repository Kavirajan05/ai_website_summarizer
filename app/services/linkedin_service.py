import json
import logging
from app.services.ai_processor import process_with_ai
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def analyze_linkedin_profile(url: str = None, profile_text: str = None) -> dict:
    """Analyzes LinkedIn profile text with simplified keys for UI compatibility."""
    text_to_analyze = profile_text
    
    if not text_to_analyze or not text_to_analyze.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting LinkedIn analysis with UI-Sync keys")

    prompt = f"""
    Analyze the following LinkedIn profile text. 
    Return ONLY a JSON object with exactly these keys:
    {{
        "score": (number 0-100),
        "headline": "Improved Headline",
        "about": "Improved About section",
        "strengths": ["strength 1", "strength 2"],
        "weaknesses": ["weakness 1", "weakness 2"],
        "suggestions": ["suggestion 1", "suggestion 2"]
    }}

    Profile Text:
    {text_to_analyze}
    """

    try:
        response_text = process_with_ai(prompt)
        
        # Check for quota
        if isinstance(response_text, str) and ("429" in response_text or "quota" in response_text.lower()):
            raise Exception("Gemini Quota Exceeded")
            
        if isinstance(response_text, dict):
            return _normalize_keys(response_text)
            
        return _normalize_keys(_parse_json(response_text))
        
    except Exception as e:
        logger.warning(f"Primary AI failed: {e}. Trying Groq fallback...")
        if settings.groq_api_key:
            try:
                client = Groq(api_key=settings.groq_api_key)
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return _normalize_keys(json.loads(response.choices[0].message.content))
            except Exception as ge:
                logger.error(f"Fallback failed: {ge}")
        
        return _static_fallback()

def _normalize_keys(data):
    """Ensures keys match what the React UI expects."""
    return {
        "score": data.get("score", 70),
        "improved_headline": data.get("headline", data.get("improved_headline", "Professional")),
        "improved_about": data.get("about", data.get("improved_about", "Experienced professional.")),
        "strengths": data.get("strengths", []),
        "weaknesses": data.get("weaknesses", []),
        "suggestions": data.get("suggestions", [])
    }

def _parse_json(text):
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)

def _static_fallback():
    return {
        "score": 60,
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional focused on growth.",
        "strengths": ["Background in industry"],
        "weaknesses": ["AI currently overloaded"],
        "suggestions": ["Try again in 5 minutes"]
    }
