import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_document
from services.email_service import send_html_email

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Summarizer API",
    description="Extracts text from PDFs, summarizes them into HTML, and sends via email.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/doc-summarizer", status_code=status.HTTP_200_OK)
async def summarize_doc_endpoint(
    email: EmailStr = Form(...),
    file: UploadFile = File(...)
):
    """
    Accepts a PDF file and email address, extracts text, summarizes it, and sends the HTML summary.
    """
    # 1. Validate File Type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported."
        )

    try:
        logger.info(f"Received summarization request for {email} with file {file.filename}")
        
        # 2. Read File Content
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty."
            )

        # 3. Extract Text
        text = await extract_text_from_pdf(content)
        
        # 4. Summarize Text
        html_summary = await summarize_document(text)
        
        # 5. Send Email
        await send_html_email(str(email), "Here is your Summary !!", html_summary)
        
        return {
            "message": "Summary sent successfully",
            "email": str(email)
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {str(e)}"
        )

@app.get("/")
async def health_check():
    return {"status": "Document Summarizer API is running"}
