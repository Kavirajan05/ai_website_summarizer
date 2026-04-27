import os
import json
import logging
import asyncio
import glob
from playwright.async_api import async_playwright
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

def find_nix_chromium():
    """Finds the chromium binary in the Nix store by searching for it."""
    # Look for the headless shell in the nix store
    nix_path = "/nix/store/*/bin/chrome-headless-shell"
    matches = glob.glob(nix_path)
    if matches:
        logger.info(f"Found Nix Chromium at: {matches[0]}")
        return matches[0]
    
    # Also check for standard chromium
    nix_path_alt = "/nix/store/*/bin/chromium"
    matches_alt = glob.glob(nix_path_alt)
    if matches_alt:
        logger.info(f"Found Nix Chromium (alt) at: {matches_alt[0]}")
        return matches_alt[0]
        
    return None

async def fetch_profile_text(url: str) -> str:
    """Scrapes a LinkedIn profile using Playwright with Smart Finder."""
    logger.info(f"Starting Smart Playwright fetch for {url}")
    
    try:
        async with async_playwright() as p:
            # Smart Finder: Try to find the nix-installed browser first
            executable_path = find_nix_chromium()
            
            if executable_path:
                browser = await p.chromium.launch(executable_path=executable_path, headless=True)
            else:
                # Fallback to standard launch (and self-healing if needed)
                try:
                    browser = await p.chromium.launch(headless=True)
                except Exception as le:
                    if "executable doesn't exist" in str(le).lower():
                        logger.info("Browser missing! Running emergency installation...")
                        import subprocess
                        subprocess.run(["playwright", "install", "chromium"], check=True)
                        browser = await p.chromium.launch(headless=True)
                    else:
                        raise le

            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            content = await page.inner_text("body")
            await browser.close()
            
            return content[:8000]
            
    except Exception as e:
        logger.error(f"Playwright error: {str(e)}")
        raise ValueError(f"Could not scrape LinkedIn. Error: {str(e)}")

def _offline_response(profile_text):
    """Fallback offline analysis."""
    return {
        "score": 75,
        "strengths": ["Visible professional history"],
        "weaknesses": ["Could use more quantified results"],
        "suggestions": ["Add specific metrics to your bullet points"],
        "improved_headline": "Professional in their field",
        "improved_about": "Experienced professional focused on delivering high-quality results."
    }

async def analyze_linkedin_profile(url: str = None, manual_text: str = None) -> dict:
    if manual_text:
        profile_text = manual_text
    else:
        if not url:
            raise ValueError("URL is required if manual text is not provided.")
        profile_text = await fetch_profile_text(url)

    if not profile_text or not profile_text.strip():
        raise ValueError("Could not extract any text from the LinkedIn profile.")

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
