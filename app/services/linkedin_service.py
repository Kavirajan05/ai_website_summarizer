import os
import json
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def analyze_linkedin_profile(url: str = None, manual_text: str = None) -> dict:
    """Analyzes LinkedIn profile text using Gemini."""
    # Use manual text as primary input
    profile_text = manual_text
    
    if not profile_text or not profile_text.strip():
        raise ValueError("Please paste the LinkedIn profile text to analyze.")

    logger.info("Starting Gemini analysis for LinkedIn profile text")

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
    {profile_text}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Parse JSON from response
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return json.loads(text)
        
    except Exception as e:
        logger.error(f"Gemini Analysis error: {e}")
        # Fallback response
        return {
            "score": 60,
            "strengths": ["Professional background visible"],
            "weaknesses": ["Analysis failed or text too short"],
            "suggestions": ["Please try again with more detailed profile text"],
            "improved_headline": "Professional in their field",
            "improved_about": "Experienced professional."
        }
