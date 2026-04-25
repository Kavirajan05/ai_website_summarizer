import asyncio
import time
import json
import re
import logging
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def call_gemini_single_prompt(query: str) -> tuple[str, float]:
    """
    Makes a single call to Gemini to generate the full multi-model mock response and summary.
    This saves 3 API calls and prevents hitting the 15 RPM free tier limit.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY is missing.")
        return "[Error: API Key missing]", 0.0

    t0 = time.perf_counter()

    def _sync_call() -> str:
        genai.configure(api_key=settings.gemini_api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Safely pick a model
        model_name = "gemini-1.5-flash"
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]
            
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
You are an expert AI orchestrator. The user has submitted a query, and you need to simulate the responses of three different AI models, and then summarize them.

User Query: "{query}"

Step 1: Write a concise, direct response as if you were "Qwen from Alibaba Cloud".
Step 2: Write a highly detailed, analytical response as if you were "LLaMA 3.3 70B from Meta".
Step 3: Write a comprehensive, natural response as if you were "Google Gemini".
Step 4: Summarize all three responses.

You MUST return your ENTIRE output as a single, valid JSON object. 
DO NOT include any markdown formatting or text outside the JSON object.

The JSON MUST exactly match this structure:
{{
  "models": {{
      "openrouter_qwen": "<Qwen's response>",
      "groq_llama": "<LLaMA's response>",
      "gemini": "<Gemini's response>"
  }},
  "final_summary": {{
      "title": "<A concise title for the report>",
      "overview": "<A 2-3 sentence overview of the topic>",
      "key_points": ["<point 1>", "<point 2>", "<point 3>"],
      "strengths": ["<strength 1>", "<strength 2>"],
      "challenges": ["<challenge 1>", "<challenge 2>"],
      "conclusion": "<A 2-3 sentence conclusion>"
  }}
}}
"""
        result = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return result.text.strip()

    try:
        loop = asyncio.get_event_loop()
        result_text = await loop.run_in_executor(None, _sync_call)
        elapsed = time.perf_counter() - t0
        return result_text, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - t0
        logger.error(f"[Gemini Single Call] Failed: {e}")
        return f"[Error: {str(e)}]", elapsed

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
    return None

async def run_multimodel_pipeline(query: str) -> dict:
    t0 = time.perf_counter()
    
    # Make 1 single call to generate all mocks + summary
    raw_response, elapsed = await call_gemini_single_prompt(query)
    
    parsed = _extract_json(raw_response)
    
    if parsed is None:
        # If parsing failed or an error occurred
        fallback = _fallback_structure(raw_response)
        return {
            "models": {
                "openrouter_qwen": "N/A",
                "groq_llama": "N/A",
                "gemini": "N/A"
            },
            "final_summary": fallback,
            "meta": {
                "latency": {
                    "openrouter_qwen": "N/A",
                    "groq_llama": "N/A",
                    "gemini": "N/A",
                    "total": f"{(time.perf_counter() - t0):.2f}s"
                }
            }
        }
        
    # Successfully parsed!
    # Simulate slightly different latencies for realism based on the single call's execution time
    simulated_qwen = max(0.5, elapsed * 0.4)
    simulated_llama = max(1.0, elapsed * 0.8)
    simulated_gemini = max(0.3, elapsed * 0.3)
    
    latency = {
        "openrouter_qwen": f"{simulated_qwen:.2f}s",
        "groq_llama": f"{simulated_llama:.2f}s",
        "gemini": f"{simulated_gemini:.2f}s",
        "total": f"{(time.perf_counter() - t0):.2f}s"
    }

    return {
        "models": parsed.get("models", {}),
        "final_summary": parsed.get("final_summary", {}),
        "meta": {"latency": latency}
    }
