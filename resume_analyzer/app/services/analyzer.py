from app.services.extraction import extraction_service
from app.services.llm_service import llm_service
from app.services.email_service import email_service
from app.schemas.resume import ResumeAnalysisResult
import logging

logger = logging.getLogger(__name__)

class AnalyzerService:
    async def process_and_notify(self, file_content: bytes, filename: str, recipient_email: str):
        """
        Orchestrates the resume analysis workflow:
        1. Extract text
        2. Analyze with AI
        3. Send email report
        """
        try:
            # 1. Text Extraction
            logger.info(f"Extracting text from {filename}...")
            text = extraction_service.extract_text(file_content, filename)
            
            # 2. AI Analysis
            logger.info("Analyzing with LLM...")
            analysis_result = llm_service.analyze_resume(text)
            
            # 3. Email Notification
            logger.info(f"Sending report to {recipient_email}...")
            await email_service.send_analysis_report(recipient_email, analysis_result)
            
            logger.info("Workflow completed successfully.")
            
        except Exception as e:
            logger.error(f"Error in analyzer workflow: {str(e)}")
            # In a real production app, we might want to notify the user of the failure via email
            raise e

analyzer_service = AnalyzerService()
