from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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


def _fallback_response():
    return {
        "score": 70,
        "strengths": ["Good profile structure"],
        "weaknesses": ["Profile analysis could not be completed from the AI service"],
        "suggestions": ["Add quantified achievements", "Improve keyword density"],
        "improved_headline": "Software Engineer | Python | FastAPI | Backend",
        "improved_about": "Passionate developer focused on building reliable backend systems and practical AI tools.",
    }

def analyze_with_groq(profile_text):

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

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content or "{}"
    except Exception:
        return _offline_response(profile_text)

    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        return _offline_response(profile_text)