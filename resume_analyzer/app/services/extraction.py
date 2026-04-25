import fitz  # PyMuPDF
import docx
from typing import BinaryIO
import io
from app.utils.text_cleaner import clean_text

class ExtractionService:
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        """Extracts text from a PDF file using PyMuPDF."""
        text = ""
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        return clean_text(text)

    @staticmethod
    def extract_from_docx(file_content: bytes) -> str:
        """Extracts text from a DOCX file using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            text = "\n".join(full_text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
        return clean_text(text)

    @classmethod
    def extract_text(cls, file_content: bytes, filename: str) -> str:
        """Detects file type and extracts text."""
        if filename.lower().endswith(".pdf"):
            return cls.extract_from_pdf(file_content)
        elif filename.lower().endswith(".docx"):
            return cls.extract_from_docx(file_content)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

extraction_service = ExtractionService()
