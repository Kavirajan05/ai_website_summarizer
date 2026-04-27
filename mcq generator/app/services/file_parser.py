"""
app/services/file_parser.py

Extracts raw text from uploaded documents.
Supports: .pdf (via pdfplumber), .docx (via python-docx), .txt
"""

import io
from fastapi import UploadFile


# ── PDF ──────────────────────────────────────────────────────────────────────

async def _parse_pdf(file: UploadFile) -> str:
    """Extract text from a PDF file using pdfplumber (with PyPDF2 fallback)."""
    content = await file.read()

    # Primary: pdfplumber (better layout handling)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages_text)
        if text.strip():
            return text
    except Exception:
        pass  # Fall through to PyPDF2

    # Fallback: PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
        return text
    except Exception as exc:
        raise ValueError(f"Could not extract text from PDF: {exc}") from exc


# ── DOCX ──────────────────────────────────────────────────────────────────────

async def _parse_docx(file: UploadFile) -> str:
    """Extract text from a Word (.docx) file using python-docx."""
    content = await file.read()
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        text = "\n".join(para.text for para in doc.paragraphs)
        return text
    except Exception as exc:
        raise ValueError(f"Could not extract text from DOCX: {exc}") from exc


# ── TXT ───────────────────────────────────────────────────────────────────────

async def _parse_txt(file: UploadFile) -> str:
    """Decode a plain-text file as UTF-8 (with latin-1 fallback)."""
    content = await file.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


# ── Public API ────────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


async def extract_text(file: UploadFile) -> str:
    """
    Detect file type and delegate to the appropriate parser.

    Args:
        file: The uploaded FastAPI UploadFile object.

    Returns:
        The extracted plain-text string.

    Raises:
        ValueError: If the file type is unsupported or the document is empty.
    """
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Allowed types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if extension == ".pdf":
        text = await _parse_pdf(file)
    elif extension == ".docx":
        text = await _parse_docx(file)
    else:  # .txt
        text = await _parse_txt(file)

    if not text or not text.strip():
        raise ValueError("The uploaded document appears to be empty or unreadable.")

    return text
