import fitz  # PyMuPDF
import docx
import io
import re
import logging

logger = logging.getLogger(__name__)

def _clean_text(text: str) -> str:
    """Cleans extracted text by removing extra whitespace and non-printable chars."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")
    return text.strip()


def extract_resume_text(file_content: bytes, filename: str) -> str:
    """Detects file type and extracts text from PDF or DOCX."""
    fname = filename.lower()
    if fname.endswith(".pdf"):
        return _extract_from_pdf(file_content)
    elif fname.endswith(".docx"):
        return _extract_from_docx(file_content)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")


def _extract_from_pdf(file_content: bytes) -> str:
    """Extracts text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return _clean_text(text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def _extract_from_docx(file_content: bytes) -> str:
    """Extracts text from a DOCX using python-docx."""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        paragraphs = [para.text for para in doc.paragraphs]
        text = "\n".join(paragraphs)
        return _clean_text(text)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")
