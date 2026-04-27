import json
import io
import re
import logging
import google.generativeai as genai
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extracts text from PDF, DOCX, or TXT files."""
    lower = filename.lower()
    try:
        if lower.endswith(".pdf"):
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        elif lower.endswith(".docx"):
            import docx
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join(para.text for para in doc.paragraphs)
        elif lower.endswith(".txt"):
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                return file_content.decode("latin-1")
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    except Exception as e:
        logger.error(f"File extraction failed: {e}")
        raise ValueError(f"Could not read {filename}: {str(e)}")

async def generate_mcqs(text: str) -> dict:
    """Generates MCQs with model discovery and fallback."""
    if not text.strip():
        raise ValueError("No text provided for MCQ generation.")

    prompt = f"""
    Analyze the following document and generate 5-10 Multiple Choice Questions (MCQs).
    Return ONLY a JSON object with this structure:
    {{
        "title": "Topic Name",
        "questions": [
            {{
                "question": "The question?",
                "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
                "answer": "A",
                "explanation": "Why A is correct"
            }}
        ]
    }}

    Document:
    {text[:15000]}
    """

    # 1. Try Gemini with Auto-Discovery
    try:
        if not settings.gemini_api_key:
            raise Exception("Gemini key missing")
            
        genai.configure(api_key=settings.gemini_api_key)
        
        # Discover available models
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prefer flash, then any available
        model_name = "models/gemini-1.5-flash"
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif available_models:
            model_name = available_models[0]
            
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        
        return _parse_json(response.text)

    except Exception as e:
        logger.warning(f"Gemini failed or quota hit ({e}). Trying Groq fallback...")
        
        # 2. Try Groq Fallback
        if settings.groq_api_key:
            try:
                client = Groq(api_key=settings.groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as ge:
                logger.error(f"Groq also failed: {ge}")
        
        raise Exception(f"AI services overloaded. Last error: {str(e)[:50]}")

def _parse_json(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)
