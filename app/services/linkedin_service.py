import os
import json
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def analyze_linkedin_profile(url: str = None, profile_text: str = None) -> dict:
    """Analyzes LinkedIn profile text using Gemini with safety filters disabled."""
    text_to_analyze = profile_text
    
    if not text_to_analyze or not text_to_analyze.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting Deep Gemini analysis for LinkedIn profile")

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
        # Use flash-latest for better reliability
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Disable safety filters to prevent blocking professional profiles
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        logger.error(f"Gemini Deep Analysis failed: {str(e)}")
        # Fallback response
        return {
            "score": 60,
            "strengths": ["Professional background visible"],
            "weaknesses": [f"AI Connection Error: {str(e)[:50]}..."],
            "suggestions": ["Ensure your Gemini API key is valid in Railway settings"],
            "improved_headline": "Professional in their field",
            "improved_about": "Experienced professional."
        }
