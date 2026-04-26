import json
import logging
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

def fetch_profile_text(url: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    logger.info(f"Starting selenium fetch for {url}")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.warning(f"ChromeDriverManager failed, attempting system chromium: {e}")
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)

    body = driver.find_element(By.TAG_NAME, "body").text
    driver.quit()
    return body[:8000]

def _keyword_present(text, keywords):
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)

def _offline_response(profile_text):
    text = profile_text or ""
    strengths = []
    weaknesses = []
    suggestions = []

    if _keyword_present(text, ["python", "java", "javascript", "react", "fastapi", "django", "flask"]):
        strengths.append("Clear technical stack mentioned")
    if _keyword_present(text, ["engineer", "developer", "analyst", "manager", "consultant"]):
        strengths.append("Role identity is visible")
    if re.search(r"\b\d+%\b|\b\d+\b", text):
        strengths.append("Contains measurable details")
    if _keyword_present(text, ["lead", "led", "built", "improved", "designed", "delivered"]):
        strengths.append("Shows action-oriented language")

    if not strengths:
        strengths.append("Profile has room for stronger positioning")

    if not re.search(r"\b\d+%\b|\b\d+\b", text):
        weaknesses.append("No quantified achievements found")
        suggestions.append("Add 2-3 metrics such as growth, speed, revenue, or scale")
    if len(text.split()) < 120:
        weaknesses.append("Profile text is too short to build trust quickly")
        suggestions.append("Expand the about section with role, impact, and proof")
    if not _keyword_present(text, ["python", "java", "javascript", "react", "fastapi", "django", "flask", "sql"]):
        weaknesses.append("Missing clear keyword signals for recruiters")
        suggestions.append("Repeat your target role keywords naturally in headline and about")
    if not _keyword_present(text, ["lead", "built", "delivered", "improved", "designed", "optimized"]):
        weaknesses.append("Not enough impact-focused language")
        suggestions.append("Start bullet points with strong verbs and outcomes")

    if not weaknesses:
        weaknesses.append("Profile would benefit from tighter positioning")
    if not suggestions:
        suggestions.extend([
            "Tighten the headline around one target role",
            "Add one proof point per job or project",
        ])

    return {
        "score": 78 if len(strengths) >= 2 else 68,
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "suggestions": suggestions[:4],
        "improved_headline": "Software Engineer | Python | FastAPI | Backend",
        "improved_about": "I build practical backend systems, automate repetitive work, and focus on measurable outcomes using Python and modern web tools.",
    }

async def analyze_linkedin_profile(url: str) -> dict:
    # 1. Fetch text (let errors bubble up so frontend can see if Selenium fails!)
    profile_text = fetch_profile_text(url)

    if not profile_text.strip():
        raise ValueError("Could not extract any text from the LinkedIn profile page.")

    # 2. Analyze using Groq (Original Workflow)
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is not set. Falling back to offline text analysis.")
        return _offline_response(profile_text)

    prompt = f"""
You are a LinkedIn expert.

Analyze the profile and return STRICT JSON:

{{
 "score": number,
 "strengths": [],
 "weaknesses": [],
 "suggestions": [],
 "improved_headline": "",
 "improved_about": ""
}}

Profile:
{profile_text}
"""

    client = Groq(api_key=settings.groq_api_key)
    
    try:
        # We need to run the synchronous Groq client in an executor
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _call_groq():
            return client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
        response = await loop.run_in_executor(None, _call_groq)
        content = response.choices[0].message.content or "{}"
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return _offline_response(profile_text)

    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"JSON Parsing error: {e}")
        return _offline_response(profile_text)
