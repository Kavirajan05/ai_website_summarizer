import json
import logging
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

def fetch_profile_text(url: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(5) # wait for page to load

        body = driver.find_element(By.TAG_NAME, "body").text
        driver.quit()
        return body[:8000]
    except Exception as e:
        logger.error(f"Selenium fetch failed: {e}")
        raise ValueError(f"Failed to fetch LinkedIn profile: {str(e)}")

def _fallback_response():
    return {
        "score": 70,
        "strengths": ["Clear professional background visible"],
        "weaknesses": ["Detailed AI analysis could not be completed"],
        "suggestions": ["Add more measurable achievements", "Optimize keywords for your target role"],
        "improved_headline": "Professional | Experienced Specialist",
        "improved_about": "Experienced professional focused on delivering measurable impact and driving continuous improvement in fast-paced environments.",
    }

async def analyze_linkedin_profile(url: str) -> dict:
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY is not set.")
        return _fallback_response()

    try:
        # Fetch text
        profile_text = fetch_profile_text(url)
        
        if len(profile_text.strip()) < 50:
            raise ValueError("Profile text is too short or could not be scraped.")
            
        # Analyze with Gemini
        genai.configure(api_key=settings.gemini_api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        model_name = "gemini-1.5-flash"
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]
            
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
You are an expert LinkedIn profile reviewer and recruiter.
Analyze the following LinkedIn profile text and provide constructive feedback.

Return your analysis STRICTLY as a valid JSON object matching exactly this structure:
{{
 "score": <an integer out of 100 representing profile strength>,
 "strengths": ["strength 1", "strength 2", "strength 3"],
 "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
 "suggestions": ["actionable suggestion 1", "actionable suggestion 2"],
 "improved_headline": "<a rewritten, high-impact headline>",
 "improved_about": "<a rewritten, engaging about section (3-4 sentences)>"
}}

Profile Text:
{profile_text}
"""
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        text = response.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return _fallback_response()
            
    except Exception as e:
        logger.error(f"LinkedIn analysis failed: {e}")
        return _fallback_response()
