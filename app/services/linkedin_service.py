import json
import logging
from app.services.ai_processor import process_with_ai

logger = logging.getLogger(__name__)

async def analyze_linkedin_profile(url: str = None, profile_text: str = None) -> dict:
    """Analyzes LinkedIn profile text using the project's standard AI processor."""
    text_to_analyze = profile_text
    
    if not text_to_analyze or not text_to_analyze.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting LinkedIn analysis using standard AI Processor")

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

    try:
        # Use the working process_with_ai function that all other services use
        response_text = await process_with_ai(prompt)
        
        # Parse JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(response_text)
        
    except Exception as e:
        logger.error(f"LinkedIn AI Processor analysis failed: {str(e)}")
        # Fallback response
        return {
            "score": 60,
            "strengths": ["Professional background visible"],
            "weaknesses": [f"AI Error: {str(e)[:50]}..."],
            "suggestions": ["Ensure your AI service is running correctly"],
            "improved_headline": "Professional in their field",
            "improved_about": "Experienced professional."
        }
