"""
app/services/gemini_service.py

Handles all interactions with the Google Gemini API.
Uses the current `google-genai` SDK (replaces deprecated `google-generativeai`).
Provides a single public function: generate_questions(text) -> List[str]
"""

import os
import re
from typing import List

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load .env file (no-op in production where vars are set via Railway/OS)
load_dotenv()

# ── Initialise Gemini client once at module import time ───────────────────────

_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not _API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY environment variable is not set. "
        "Add it to your .env file or Railway environment."
    )

_client = genai.Client(api_key=_API_KEY)

# gemini-2.5-flash: available model since 1.5 is 404, and 2.0-flash was out of quota
_MODEL_NAME = "gemini-2.5-flash"

# ── Prompt template ───────────────────────────────────────────────────────────

_PROMPT_TEMPLATE = """\
Read the following document carefully and generate between 5 and 10 high-quality, \
meaningful questions that test a reader's understanding of the content.

Guidelines:
- Vary the difficulty: include easy, medium, and hard questions.
- Avoid repetition or trivially similar questions.
- Questions should be self-contained and answerable from the document alone.
- Output ONLY the numbered list of questions, one per line, with no extra text.

Document:
{document_text}
"""

# ── Question parser ───────────────────────────────────────────────────────────

def _parse_questions(raw: str) -> List[str]:
    """
    Convert a numbered list response from Gemini into a clean Python list.

    Handles formats like:
        1. What is ...?
        1) What is ...?
        - What is ...?
    """
    questions: List[str] = []
    for line in raw.splitlines():
        # Strip leading bullets / numbers
        line = re.sub(r"^\s*(\d+[\.\)]\s*|[-•]\s*)", "", line).strip()
        if line:
            questions.append(line)
    return questions

# ── Public API ────────────────────────────────────────────────────────────────

async def generate_questions(text: str) -> List[str]:
    """
    Send cleaned document text to Gemini and return generated questions.

    Args:
        text: The cleaned, truncated document content.

    Returns:
        A list of question strings.

    Raises:
        RuntimeError: If the Gemini API call fails or returns an empty response.
    """
    prompt = _PROMPT_TEMPLATE.format(document_text=text)

    try:
        response = _client.models.generate_content(
            model=_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,      # Balanced creativity
                max_output_tokens=1024,
            ),
        )
        raw_text: str = response.text or ""
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    questions = _parse_questions(raw_text)

    if not questions:
        raise RuntimeError(
            "Gemini returned an empty or unparseable response. "
            "Please try again or check your API key quota."
        )

    return questions
