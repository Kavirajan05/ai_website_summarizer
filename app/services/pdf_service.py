import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extracts text from PDF binary content using PyMuPDF.
    """
    try:
        # Open PDF from memory
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        
        doc.close()
        
        if not text.strip():
            logger.warning("The PDF contains no extractable text.")
            return ""
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
