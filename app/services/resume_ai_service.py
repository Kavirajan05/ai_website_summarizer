import json
import re
import io
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


def _clean_text(text: str) -> str:
    """Cleans extracted text by removing extra whitespace and non-printable characters."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")
    return text.strip()


def extract_text_from_resume(file_content: bytes, filename: str) -> str:
    """Extracts text from a PDF or DOCX resume file."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return _clean_text(text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    elif lower.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_content))
            full_text = [para.text for para in doc.paragraphs]
            return _clean_text("\n".join(full_text))
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")


async def analyze_resume_with_ai(resume_text: str) -> dict:
    """
    Analyzes resume text using Google Gemini and returns structured JSON.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    if not resume_text.strip():
        raise ValueError("No text could be extracted from the resume.")

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and senior HR professional.
    Analyze the following resume text and provide a comprehensive, structured analysis in JSON format.

    Resume Text:
    {resume_text[:15000]}

    Your response MUST be a valid JSON object with EXACTLY this structure:
    {{
        "name": "Full Name of the candidate",
        "email": "candidate@email.com",
        "skills": ["Skill 1", "Skill 2", "Skill 3"],
        "experience": "A 2-3 sentence summary of the candidate's work experience and notable roles.",
        "education": "A 1-2 sentence summary of the candidate's educational background.",
        "ats_score": 78,
        "missing_skills": ["Missing Skill 1", "Missing Skill 2"],
        "suggestions": ["Actionable suggestion 1", "Actionable suggestion 2", "Actionable suggestion 3"]
    }}

    Rules:
    - ats_score must be an integer between 0 and 100, reflecting resume quality and keyword density.
    - missing_skills should be relevant industry keywords absent from the resume.
    - suggestions must be specific, actionable, and professional.
    - ONLY return the JSON object. No markdown fences, no extra text.
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

        logger.info(f"Using model: {model_name} for resume analysis")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        text_resp = response.text.strip()

        # Strip markdown fences if present
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[-1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[1].split("```")[0].strip()

        data = json.loads(text_resp)
        return data

    except Exception as e:
        logger.error(f"Resume AI Analysis failed: {str(e)}")
        raise ValueError(f"AI Analysis failed: {str(e)}")
