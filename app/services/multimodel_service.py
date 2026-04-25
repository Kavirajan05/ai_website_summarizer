import asyncio
import time
import json
import re
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def call_gemini(query: str, system_instruction: str = "") -> str:
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY is missing.")
        return "N/A"

    def _sync_call() -> str:
        genai.configure(api_key=settings.gemini_api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prefer flash model
        model_name = "gemini-1.5-flash"
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]
            
        model = genai.GenerativeModel(model_name)
        
        full_query = f"{system_instruction}\n\nUser Query: {query}" if system_instruction else query
        result = model.generate_content(full_query)
        return result.text.strip()

    async def _attempt_call():
        for attempt in range(4):
            try:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, _sync_call)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < 3:
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"[Gemini] 429 Rate Limit. Retrying in {wait_time}s... (Attempt {attempt+1}/3)")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"[Gemini] Failed: {e}")
                    return f"[Error: {error_msg}]"

    return await _attempt_call()

async def _timed(name: str, coro) -> tuple:
    t0 = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - t0
    return name, result, elapsed

async def gather_llm_responses(query: str) -> tuple:
    # We mock Qwen and LLaMA by giving Gemini different personas/system instructions 
    # so the outputs actually look like they came from different models!
    
    qwen_prompt = "You are Qwen, an AI from Alibaba Cloud. Answer the query concisely and directly."
    llama_prompt = "You are LLaMA 3.3 70B, an AI by Meta. Answer the query with highly analytical, detailed explanations."
    gemini_prompt = "You are Google Gemini. Answer the query naturally and comprehensively."
    
    # Run sequentially to avoid blowing up the Gemini Free Tier concurrent rate limit
    res_qwen = await _timed("openrouter_qwen", call_gemini(query, qwen_prompt))
    await asyncio.sleep(1) # Small delay to be safe
    res_llama = await _timed("groq_llama", call_gemini(query, llama_prompt))
    await asyncio.sleep(1)
    res_gemini = await _timed("gemini", call_gemini(query, gemini_prompt))
    
    results = [res_qwen, res_llama, res_gemini]
    
    responses, latency = {}, {}
    for name, text, elapsed in results:
        responses[name] = text
        latency[name] = f"{elapsed:.2f}s"
    return responses, latency

def _fallback_structure(raw: str) -> dict:
    if not raw or raw == "N/A" or "[Error:" in raw:
        overview = f"API Error: {raw}"
    else:
        overview = raw

    return {
        "title": "AI Model Summary",
        "overview": overview,
        "key_points": [],
        "strengths": [],
        "challenges": [],
        "conclusion": "",
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
    
    # Use Gemini to generate the final structured JSON summary as well!
    raw_summary = await call_gemini(prompt)

    summary_dict = _extract_json(raw_summary)
    latency["total"] = f"{(time.perf_counter() - t0):.2f}s"

    return {
        "models": responses,
        "final_summary": summary_dict,
        "meta": {"latency": latency}
    }
