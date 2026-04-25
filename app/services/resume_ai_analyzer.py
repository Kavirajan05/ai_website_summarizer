import json
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


async def analyze_resume_with_ai(resume_text: str) -> dict:
    """
    Sends resume text to Gemini and returns a structured analysis dict.
    No email — result is returned directly to the caller.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    if not resume_text.strip():
        raise ValueError("No text could be extracted from the resume.")

    prompt = f"""
You are an expert ATS (Applicant Tracking System) analyst and senior HR professional.
Analyze the following resume and return a detailed assessment as a JSON object.

Resume Text:
{resume_text[:20000]}

Your response MUST be a valid JSON object with EXACTLY this structure:
{{
    "name": "Candidate full name",
    "email": "Candidate email address",
    "phone": "Candidate phone number or N/A",
    "skills": ["Skill 1", "Skill 2", "Skill 3"],
    "experience": "Concise 2-3 sentence summary of total work experience",
    "education": "Concise summary of educational background",
    "ats_score": 78,
    "missing_skills": ["Missing Skill 1", "Missing Skill 2"],
    "suggestions": [
        "Actionable suggestion 1",
        "Actionable suggestion 2",
        "Actionable suggestion 3"
    ],
    "strengths": ["Strength 1", "Strength 2"],
    "overall_verdict": "Brief 1-2 sentence overall assessment of the candidate."
}}

Rules:
- ats_score must be an integer between 0 and 100.
- missing_skills should list relevant keywords typically expected for this candidate's career path.
- suggestions must be specific and actionable (not generic).
- strengths should highlight what makes this resume stand out.
- ONLY return the JSON object. No markdown, no code fences, no extra text.
"""

    try:
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]

        # Prefer flash model
        model_name = "gemini-1.5-flash"
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]

        logger.info(f"Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        text_resp = response.text.strip()

        # Strip markdown code fences if present
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[-1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[1].strip()

        data = json.loads(text_resp)
        return data

    except Exception as e:
        logger.error(f"Resume AI analysis failed: {str(e)}")
        raise ValueError(f"AI analysis failed: {str(e)}")
