import json
import io
import re
import logging
from typing import List
from app.services.ai_processor import process_with_ai

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
    """Generates MCQs using the standard project AI processor."""
    if not text.strip():
        raise ValueError("No text provided for MCQ generation.")

    prompt = f"""
    Based on the following document content, generate 5-10 high-quality Multiple Choice Questions (MCQs).
    Each question MUST have 4 options (A, B, C, D) and 1 correct answer.
    
    You MUST format your output strictly as a JSON object like this:
    {{
        "title": "Topic of the MCQs",
        "questions": [
            {{
                "question": "The question text?",
                "options": {{
                    "A": "Option text",
                    "B": "Option text",
                    "C": "Option text",
                    "D": "Option text"
                }},
                "answer": "A",
                "explanation": "Brief explanation of why A is correct"
            }}
        ]
    }}

    Document Content:
    {text[:15000]}
    """

    try:
        # Use the project's standard processor for model fallback & consistency
        response_text = process_with_ai(prompt)
        
        # Parse JSON
        if isinstance(response_text, dict):
            return response_text
            
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(response_text)
        
    except Exception as e:
        logger.error(f"MCQ Generation AI failure: {e}")
        raise Exception(f"AI failed to generate MCQs: {str(e)}")
