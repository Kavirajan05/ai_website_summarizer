"""
main.py — FastAPI application entry point
Multi-Model AI Summarization API (Enhanced — v2)
"""

import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, BackgroundTasks, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from utils.logger import setup_logger
from utils.formatter import text_to_html
from services.llm import gather_llm_responses, merge_responses
from services.summarizer import summarize_combined
from services.email import send_html_email

# ── Logging ────────────────────────────────────────────────────────────────────

setup_logger()

# ── Rate Limiter ───────────────────────────────────────────────────────────────

RATE_LIMIT = os.getenv("RATE_LIMIT_PER_MINUTE", "10")
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT}/minute"])

# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Multi-Model AI Summarization API v2 starting up")
    yield
    logger.info("🛑 API shutting down")

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Model AI Summarization API",
    description=(
        "Queries OpenRouter (Qwen), Groq (LLaMA 3.3 70B), and Google Gemini **in parallel**, "
        "aggregates all responses, produces a structured JSON summary, and optionally "
        "delivers an HTML email — all in a single API call."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Schemas ─────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    query: str
    email: str | None = None
    send_email: bool = False

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query must not be empty")
        if len(v) > 2000:
            raise ValueError("query must be 2000 characters or fewer")
        return v


class FinalSummary(BaseModel):
    title: str
    overview: str
    key_points: list[str]
    strengths: list[str]
    challenges: list[str]
    conclusion: str


class LatencyMeta(BaseModel):
    openrouter_qwen: str
    groq_llama: str
    gemini: str
    total: str


class ModelsMeta(BaseModel):
    openrouter_qwen: str
    groq_llama: str
    gemini: str


class SummarizeResponse(BaseModel):
    status: str
    input: str
    models: ModelsMeta
    final_summary: FinalSummary
    email_sent: bool
    meta: dict


# ── Core pipeline ──────────────────────────────────────────────────────────────

async def run_pipeline(query: str) -> tuple[dict, dict, dict]:
    """
    Run the full multi-model pipeline. Returns:
      (model_responses, latency, structured_summary)
    """
    t0 = time.perf_counter()

    # Step 1 — parallel LLM calls with per-model timing
    responses, latency = await gather_llm_responses(query)

    total_elapsed = time.perf_counter() - t0

    # Step 2 — merge
    combined = merge_responses(responses)

    # Step 3 — structured summarization
    summary_dict = await summarize_combined(combined)

    total_elapsed_final = time.perf_counter() - t0
    latency["total"] = f"{total_elapsed_final:.2f}s"

    return responses, latency, summary_dict


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "Multi-Model AI Summarization API",
        "version": "2.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/summarize", tags=["Summarization"])
@limiter.limit(f"{RATE_LIMIT}/minute")
async def summarize(
    request: Request,
    body: SummarizeRequest,
    background_tasks: BackgroundTasks,
):
    """
    **Main endpoint** — runs all three LLMs in parallel and returns the full
    structured result immediately (no waiting for email).

    - Each model's response is included in `models`
    - A structured JSON summary is in `final_summary`
    - Per-model latency is in `meta.latency`
    - Email is sent in the background **only** if `send_email=true` and `email` is provided
    """
    logger.info(
        f"[POST /summarize] query={body.query[:60]!r} "
        f"email={body.email} send_email={body.send_email}"
    )

    try:
        responses, latency, summary_dict = await run_pipeline(body.query)
    except Exception as exc:
        logger.exception(f"[/summarize] Pipeline failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    # Optional background email
    email_queued = False
    if body.send_email and body.email:
        try:
            html_body = text_to_html(
                f"## {summary_dict.get('title', 'Summary')}\n\n"
                + summary_dict.get("overview", "")
                + "\n\n## Key Points\n"
                + "\n".join(f"- {p}" for p in summary_dict.get("key_points", []))
                + "\n\n## Conclusion\n"
                + summary_dict.get("conclusion", "")
            )
            background_tasks.add_task(
                send_html_email,
                to_address=body.email,
                subject="🤖 AI Summary Report",
                html_body=html_body,
            )
            email_queued = True
            logger.info(f"[/summarize] Email queued for {body.email}")
        except Exception as exc:
            logger.error(f"[/summarize] Email queueing failed: {exc}")
    elif body.send_email and not body.email:
        logger.warning("[/summarize] send_email=true but no email address provided")

    return {
        "status": "success",
        "input": body.query,
        "models": {
            "openrouter_qwen": responses.get("openrouter_qwen", ""),
            "groq_llama":      responses.get("groq_llama", ""),
            "gemini":          responses.get("gemini", ""),
        },
        "final_summary": {
            "title":       summary_dict.get("title", ""),
            "overview":    summary_dict.get("overview", ""),
            "key_points":  summary_dict.get("key_points", []),
            "strengths":   summary_dict.get("strengths", []),
            "challenges":  summary_dict.get("challenges", []),
            "conclusion":  summary_dict.get("conclusion", ""),
        },
        "email_sent": email_queued,
        "meta": {
            "latency": latency,
            "models_used": {
                "openrouter": "qwen/qwen3-coder:free",
                "groq":       "llama-3.3-70b-versatile",
                "gemini":     "gemini-1.5-flash",
            },
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "An internal server error occurred."},
    )


# ── Dev entrypoint ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
