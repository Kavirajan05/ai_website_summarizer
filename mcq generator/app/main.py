"""
app/main.py

FastAPI application entry point.
- Configures CORS so any frontend (React, Vue, etc.) can call the API.
- Mounts the question-generator router.
- Provides a health-check endpoint at GET /.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.question_generator import router as question_router

# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="MCQ / Question Generator API",
    description=(
        "Upload a PDF, TXT, or DOCX document and receive AI-generated "
        "questions powered by Google Gemini."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow all origins in development; restrict to your frontend domain in prod.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Replace with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(question_router, tags=["Question Generation"])

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def health_check():
    """Simple health-check endpoint used by Railway and uptime monitors."""
    return {"status": "ok", "service": "MCQ Question Generator API"}


# ── Dev entrypoint ────────────────────────────────────────────────────────────
# Run locally with:  python -m app.main
# Or via uvicorn:    uvicorn app.main:app --reload --port 8000

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
