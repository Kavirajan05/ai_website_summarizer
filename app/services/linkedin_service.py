import os
import json
import logging
import asyncio
from playwright.async_api import async_playwright
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def fetch_profile_text(url: str) -> str:
    """Scrapes a LinkedIn profile using Playwright."""
    logger.info(f"Starting Playwright fetch for {url}")
    
    try:
        async with async_playwright() as p:
            # Launch browser (Path is controlled by env var in nixpacks.toml)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            # Navigate to URL
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for content to load
            await asyncio.sleep(5)
            
            # Extract body text
            content = await page.inner_text("body")
            await browser.close()
            
            return content[:8000]
            
    except Exception as e:
        logger.error(f"Playwright error: {str(e)}")
        if "executable doesn't exist" in str(e).lower():
            raise ValueError("Railway Deployment Error: Chromium is still installing. Please wait for the build to finish or use 'Paste Profile Text'.")
        raise ValueError(f"Could not scrape LinkedIn. Error: {str(e)}")

def _offline_response(profile_text):
    """Fallback offline analysis if Groq fails."""
    # Simple keyword-based scoring
    text = (profile_text or "").lower()
    score = 70
    strengths = ["Visible professional history"]
    weaknesses = ["Could use more quantified results"]
    suggestions = ["Add specific metrics to your bullet points"]
    
    if "python" in text or "fastapi" in text:
        strengths.append("Strong technical keywords detected")
        score += 5
        
    return {
        "score": min(score, 100),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional focused on delivering high-quality results."
    }

async def analyze_linkedin_profile(url: str = None, manual_text: str = None) -> dict:
    # 1. Get profile text (either from scraping or manual input)
    if manual_text:
        profile_text = manual_text
        logger.info("Using manually provided profile text for analysis")
    else:
        if not url:
            raise ValueError("URL is required if manual text is not provided.")
        profile_text = await fetch_profile_text(url)

    if not profile_text or not profile_text.strip():
        raise ValueError("Could not extract any text from the LinkedIn profile.")

    # 2. Analyze using Groq
    if not settings.groq_api_key:
        return _offline_response(profile_text)

    prompt = f"""
    Analyze this LinkedIn profile and return STRICT JSON with score (0-100), strengths (list), weaknesses (list), suggestions (list), improved_headline, and improved_about.
    
    Profile Text:
    {profile_text}
    """

    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return _offline_response(profile_text)
