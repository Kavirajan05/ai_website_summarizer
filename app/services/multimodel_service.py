import asyncio
import time
import json
import re
import httpx
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OPENROUTER_MODEL = "qwen/qwen3-coder:free"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"
HTTP_TIMEOUT = 60.0

async def call_openrouter(query: str) -> str:
    if not settings.openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY is missing.")
        return "N/A"

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "MultiModel AI Hub",
    }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"[OpenRouter] Failed: {e}")
        return f"[Error: {str(e)}]"

async def call_groq(query: str) -> str:
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is missing.")
        return "N/A"

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.post(GROQ_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"[Groq] Failed: {e}")
        return f"[Error: {str(e)}]"

async def call_gemini(query: str) -> str:
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY is missing.")
        return "N/A"

    def _sync_call() -> str:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        result = model.generate_content(query)
        return result.text.strip()

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)
    except Exception as e:
        logger.error(f"[Gemini] Failed: {e}")
        return f"[Error: {str(e)}]"

async def _timed(name: str, coro) -> tuple:
    t0 = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - t0
    return name, result, elapsed

async def gather_llm_responses(query: str) -> tuple:
    results = await asyncio.gather(
        _timed("openrouter_qwen", call_openrouter(query)),
        _timed("groq_llama", call_groq(query)),
        _timed("gemini", call_gemini(query)),
    )
    responses, latency = {}, {}
    for name, text, elapsed in results:
        responses[name] = text
        latency[name] = f"{elapsed:.2f}s"
    return responses, latency

def _fallback_structure(raw: str) -> dict:
    return {
        "title": "AI Model Summary",
        "overview": raw[:300] if raw else "Summary unavailable.",
        "key_points": [],
        "strengths": [],
        "challenges": [],
        "conclusion": raw[-200:] if len(raw) > 300 else "",
    }

def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return _fallback_structure(text)

SUMMARY_PROMPT = """You are a professional technical writer. Based on the combined AI responses below, produce a structured summary.
IMPORTANT: Reply with ONLY valid JSON — no markdown fences, no extra text.
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

async def run_multimodel_pipeline(query: str) -> dict:
    t0 = time.perf_counter()
    responses, latency = await gather_llm_responses(query)
    
    combined = (
        f"OpenRouter (Qwen):\n{responses.get('openrouter_qwen', 'N/A')}\n\n"
        f"Groq (LLaMA 3.3 70B):\n{responses.get('groq_llama', 'N/A')}\n\n"
        f"Google Gemini:\n{responses.get('gemini', 'N/A')}"
    )

    prompt = SUMMARY_PROMPT.format(combined=combined)
    
    # Try OpenRouter first for the structured JSON
    raw_summary = await call_openrouter(prompt)
    if "[Error:" in raw_summary or raw_summary == "N/A":
        # Fallback to Groq
        raw_summary = await call_groq(prompt)
        if "[Error:" in raw_summary or raw_summary == "N/A":
             raw_summary = ""

    summary_dict = _extract_json(raw_summary)
    latency["total"] = f"{(time.perf_counter() - t0):.2f}s"

    return {
        "models": responses,
        "final_summary": summary_dict,
        "meta": {"latency": latency}
    }
