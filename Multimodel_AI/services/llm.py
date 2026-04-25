"""
services/llm.py — Async calls to OpenRouter, Groq, and Google Gemini
with retry logic, per-model latency tracking, and optional response ranking.
"""

import os
import time
import asyncio
import httpx
import google.generativeai as genai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
)
from loguru import logger


def _is_retryable_http_error(exc: BaseException) -> bool:
    """Retry on 429 Too Many Requests and any 5xx server error."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False


# ── Configuration ─────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OPENROUTER_MODEL = "qwen/qwen3-coder:free"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"

HTTP_TIMEOUT = 60.0


# ── Retry decorator ────────────────────────────────────────────────────────────

def _retry_decorator():
    """Retry on network errors AND on HTTP 429/5xx, with exponential back-off."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=3, max=30),
        retry=(
            retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
            | retry_if_exception(_is_retryable_http_error)
        ),
    )


# ── OpenRouter ─────────────────────────────────────────────────────────────────

@_retry_decorator()
async def call_openrouter(query: str, model: str = OPENROUTER_MODEL) -> str:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://multimodel-ai-api.local",
        "X-Title": "MultiModel AI Summarizer",
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        logger.info(f"[OpenRouter] Sending request | model={model}")
        response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"].strip()
    logger.info(f"[OpenRouter] Response received ({len(text)} chars)")
    return text


# ── Groq ───────────────────────────────────────────────────────────────────────

@_retry_decorator()
async def call_groq(query: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set.")

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        logger.info(f"[Groq] Sending request | model={GROQ_MODEL}")
        response = await client.post(GROQ_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"].strip()
    logger.info(f"[Groq] Response received ({len(text)} chars)")
    return text


# ── Google Gemini ──────────────────────────────────────────────────────────────

async def call_gemini(query: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    def _sync_call() -> str:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"[Gemini] Sending request | model={GEMINI_MODEL}")
        result = model.generate_content(query)
        return result.text.strip()

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _sync_call)
    logger.info(f"[Gemini] Response received ({len(text)} chars)")
    return text


# ── Timed wrapper ──────────────────────────────────────────────────────────────

async def _timed(name: str, coro) -> tuple[str, str, float]:
    """
    Run a coroutine and return (name, result_text, elapsed_seconds).
    On failure, result_text is an error description.
    """
    t0 = time.perf_counter()
    try:
        result = await coro
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.error(f"[{name}] Failed after {elapsed:.2f}s: {exc}")
        return name, f"[Error: {exc}]", elapsed
    elapsed = time.perf_counter() - t0
    logger.info(f"[{name}] Completed in {elapsed:.2f}s")
    return name, result, elapsed


# ── Parallel gather with latency ───────────────────────────────────────────────

async def gather_llm_responses(query: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Call all three LLMs in parallel with per-model latency timing.

    Returns:
        responses: dict  {"openrouter_qwen": text, "groq_llama": text, "gemini": text}
        latency:   dict  {"openrouter_qwen": "1.23s", ...}
    """
    results = await asyncio.gather(
        _timed("openrouter_qwen", call_openrouter(query)),
        _timed("groq_llama",      call_groq(query)),
        _timed("gemini",          call_gemini(query)),
    )

    responses: dict[str, str] = {}
    latency: dict[str, str] = {}
    for name, text, elapsed in results:
        responses[name] = text
        latency[name] = f"{elapsed:.2f}s"

    return responses, latency


def merge_responses(responses: dict[str, str]) -> str:
    """Combine individual LLM responses into a labelled block for summarization."""
    return (
        f"OpenRouter (Qwen):\n{responses.get('openrouter_qwen', 'N/A')}\n\n"
        f"Groq (LLaMA 3.3 70B):\n{responses.get('groq_llama', 'N/A')}\n\n"
        f"Google Gemini:\n{responses.get('gemini', 'N/A')}"
    )


def rank_responses(responses: dict[str, str]) -> list[tuple[str, str]]:
    """Return responses sorted by length (longest = most detailed) descending."""
    return sorted(responses.items(), key=lambda kv: len(kv[1]), reverse=True)
