import json
import logging
from app.services.ai_processor import process_with_ai
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def analyze_linkedin_profile(url: str = None, profile_text: str = None) -> dict:
    """Analyzes LinkedIn profile text using Gemini with Groq fallback."""
    text_to_analyze = profile_text
    
    if not text_to_analyze or not text_to_analyze.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting LinkedIn analysis with Multi-AI fallback")

    prompt = f"""
    You are an expert LinkedIn Profile Optimizer. Analyze the following profile text and provide a detailed optimization report.
    
    Return the response in STRICT JSON format with exactly these keys:
    {{
        "score": (number between 0-100),
        "strengths": ["list of 3-4 strengths"],
        "weaknesses": ["list of 3-4 weaknesses"],
        "suggestions": ["3-4 specific actionable tips"],
        "improved_headline": "A professional, high-impact headline",
        "improved_about": "A compelling, first-person 'About' section"
    }}

    Profile Text:
    {text_to_analyze}
    """

    # Try Gemini first (via standard processor)
    try:
        response_text = process_with_ai(prompt)
        
        # Check if quota exceeded in the response text
        if isinstance(response_text, str) and ("429" in response_text or "quota" in response_text.lower()):
            raise Exception("Gemini Quota Exceeded")
            
        if isinstance(response_text, dict):
            return response_text
            
        return _parse_json(response_text)
        
    except Exception as gemini_err:
        logger.warning(f"Gemini failed or quota exceeded: {gemini_err}. Trying Groq fallback...")
        
        # Fallback to Groq if key exists
        if settings.groq_api_key:
            try:
                client = Groq(api_key=settings.groq_api_key)
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as groq_err:
                logger.error(f"Groq fallback also failed: {groq_err}")
                return _fallback_static_response(f"Gemini & Groq error: {str(groq_err)[:30]}")
        
        return _fallback_static_response(f"Gemini error: {str(gemini_err)[:30]}")

def _parse_json(text):
    """Helper to clean and parse JSON strings."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)

def _fallback_static_response(error_msg):
    """Static fallback if all AI services fail."""
    return {
        "score": 60,
        "strengths": ["Professional background visible"],
        "weaknesses": [f"AI Overloaded: {error_msg}"],
        "suggestions": ["Please try again in a few minutes"],
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional."
    }
