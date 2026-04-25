"""
services/summarizer.py — Final summarization returning structured JSON
with OpenRouter primary + Groq fallback.
"""

import os
import json
import re
import httpx
from loguru import logger
from services.llm import call_openrouter, call_groq

SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", "qwen/qwen3-coder:free")

# ── Prompt ─────────────────────────────────────────────────────────────────────

SUMMARY_PROMPT_TEMPLATE = """You are a professional technical writer. Based on the combined AI responses below, produce a structured summary.

IMPORTANT: Reply with ONLY valid JSON — no markdown fences, no extra text before or after.

The JSON must have exactly these keys:
{{
  "title": "string",
  "overview": "string (2-3 sentences)",
  "key_points": ["point 1", "point 2", "point 3"],
  "strengths": ["strength 1", "strength 2"],
  "challenges": ["challenge 1", "challenge 2"],
  "conclusion": "string (2-3 sentences)"
}}

Combined AI Responses:
{combined}
"""

# ── Fallback structure when parsing fails ──────────────────────────────────────

def _fallback_structure(raw: str) -> dict:
    return {
        "title": "AI Model Summary",
        "overview": raw[:300] if raw else "Summary unavailable.",
        "key_points": [],
        "strengths": [],
        "challenges": [],
        "conclusion": raw[-200:] if len(raw) > 300 else "",
    }


# ── JSON extraction ────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """
    Safely parse a JSON object from the LLM response.
    Handles common issues: markdown fences, leading/trailing prose.
    """
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("[Summarizer] Could not parse JSON — using fallback structure")
    return _fallback_structure(text)


# ── Public API ─────────────────────────────────────────────────────────────────

async def summarize_combined(combined: str) -> dict:
    """
    Send merged LLM responses to a summarizer model.
    Returns a structured dict with: title, overview, key_points,
    strengths, challenges, conclusion.

    Falls back to Groq if OpenRouter returns 429.
    """
    prompt = SUMMARY_PROMPT_TEMPLATE.format(combined=combined)
    raw: str | None = None

    # Primary: OpenRouter
    try:
        logger.info("[Summarizer] Trying OpenRouter as primary summarizer")
        raw = await call_openrouter(prompt, model=SUMMARIZER_MODEL)
        logger.info(f"[Summarizer] OpenRouter raw response ({len(raw)} chars)")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            logger.warning("[Summarizer] OpenRouter 429 — switching to Groq fallback")
        else:
            logger.error(f"[Summarizer] OpenRouter HTTP {exc.response.status_code}")
    except Exception as exc:
        logger.error(f"[Summarizer] OpenRouter failed: {exc}")

    # Fallback: Groq
    if raw is None:
        try:
            logger.info("[Summarizer] Using Groq (LLaMA 3.3 70B) as fallback")
            raw = await call_groq(prompt)
            logger.info(f"[Summarizer] Groq raw response ({len(raw)} chars)")
        except Exception as exc:
            logger.error(f"[Summarizer] Groq fallback also failed: {exc}")
            return _fallback_structure("")

    return _extract_json(raw)
