"""
app/routes/question_generator.py

Defines the POST /generate-questions API endpoint.
Orchestrates: file upload → text extraction → cleaning → Gemini → JSON response.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.file_parser import extract_text, SUPPORTED_EXTENSIONS
from app.services.gemini_service import generate_questions
from app.utils.text_cleaner import clean

router = APIRouter()


@router.post(
    "/generate-questions",
    summary="Generate questions from an uploaded document",
    response_description="A JSON object containing a list of generated questions",
)
async def generate_questions_endpoint(
    file: UploadFile = File(..., description="PDF, TXT, or DOCX document to analyse"),
) -> JSONResponse:
    """
    Upload a document (PDF / TXT / DOCX) and receive AI-generated questions.

    **Processing steps:**
    1. Validate file extension.
    2. Extract text from the document.
    3. Clean and truncate text (max 8 000 characters).
    4. Send to Gemini → parse response into a question list.
    5. Return `{"questions": [...]}`.
    """

    # ── 1. Validate file type ─────────────────────────────────────────────────
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{extension}'. "
                f"Please upload one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        )

    # ── 2. Extract text ───────────────────────────────────────────────────────
    try:
        raw_text = await extract_text(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while parsing the document: {exc}",
        ) from exc

    # ── 3. Clean text ─────────────────────────────────────────────────────────
    clean_text = clean(raw_text, max_chars=8000)

    if not clean_text:
        raise HTTPException(
            status_code=400,
            detail="The document did not contain any readable text after processing.",
        )

    # ── 4. Generate questions via Gemini ──────────────────────────────────────
    try:
        questions = await generate_questions(clean_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {exc}",
        ) from exc

    # ── 5. Return JSON ────────────────────────────────────────────────────────
    return JSONResponse(content={"questions": questions})
