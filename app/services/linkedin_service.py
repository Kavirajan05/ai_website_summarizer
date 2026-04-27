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
    """Analyzes LinkedIn profile text using all available Gemini models."""
    text_to_analyze = profile_text
    
    if not text_to_analyze or not text_to_analyze.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting Exhaustive Gemini analysis for LinkedIn profile")

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

    # Comprehensive list of potential model names
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-pro',
        'gemini-1.0-pro',
        'models/gemini-1.5-flash',
        'models/gemini-pro'
    ]
    
    last_error = ""

    for model_name in model_names:
        try:
            logger.info(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Disable safety filters
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            # Use standard generation first, then try JSON mode if supported
            try:
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config={"response_mime_type": "application/json"}
                )
            except Exception:
                # Fallback to standard generation for older models
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings
                )
            
            # Parse response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Model {model_name} failed: {last_error}")
            continue

    # If all models fail
    logger.error(f"All Gemini models exhausted. Final error: {last_error}")
    return {
        "score": 60,
        "strengths": ["Professional background visible"],
        "weaknesses": [f"Connection error: {last_error[:50]}"],
        "suggestions": ["Please verify your Gemini API key permissions"],
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional."
    }
