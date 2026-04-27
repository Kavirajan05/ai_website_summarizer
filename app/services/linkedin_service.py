import os
import json
import logging
import asyncio
from playwright.async_api import async_playwright
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def fetch_profile_text(url: str) -> str:
    """Scrapes a LinkedIn profile using Playwright with fallback logic."""
    logger.info(f"Starting fetch for {url}")
    
    try:
        async with async_playwright() as p:
            # Standard launch
            try:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            except Exception as le:
                if "executable doesn't exist" in str(le).lower() or "shared libraries" in str(le).lower():
                    logger.info("Browser or libs missing! Attempting emergency repair...")
                    import subprocess
                    subprocess.run(["playwright", "install", "--with-deps", "chromium"], check=False)
                    browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
                else:
                    raise le

            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            # Use a realistic timeout
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            content = await page.inner_text("body")
            await browser.close()
            
            return content[:8000]
            
    except Exception as e:
        logger.error(f"Playwright error: {str(e)}")
        raise ValueError(f"Could not scrape LinkedIn profile. Error: {str(e)}")

def _offline_response(profile_text):
    """Fallback offline analysis."""
    return {
        "score": 75,
        "strengths": ["Visible professional history"],
        "weaknesses": ["Missing specific metrics"],
        "suggestions": ["Include data-driven results in your experience"],
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional dedicated to delivering quality outcomes."
    }

async def analyze_linkedin_profile(url: str = None, manual_text: str = None) -> dict:
    if manual_text:
        profile_text = manual_text
    else:
        if not url:
            raise ValueError("URL is required.")
        profile_text = await fetch_profile_text(url)

    if not profile_text or not profile_text.strip():
        raise ValueError("LinkedIn profile text is empty.")

    if not settings.groq_api_key:
        return _offline_response(profile_text)

    prompt = f"Analyze this LinkedIn profile and return JSON with score, strengths, weaknesses, suggestions, improved_headline, and improved_about.\n\nProfile Text:\n{profile_text}"

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
