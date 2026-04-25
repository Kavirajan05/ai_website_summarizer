import logging
from html import escape
from groq import Groq
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

def get_summarization_prompt(text: str) -> str:
    return f"""
    Summarize the following document into a clean, visually appealing HTML format suitable for email.
    Keep it concise and highlight key points using headings, bullet points, and emphasis.

    Document:
    {text[:15000]}  # Truncate to avoid token limits
    """


def _fallback_html_summary(text: str) -> str:
        preview = " ".join(text.split())[:400] if text.strip() else "No extractable text was available from this document."
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #102033; line-height: 1.6;">
                <div style="max-width: 760px; margin: 0 auto; padding: 24px;">
                    <h2>Document Summary</h2>
                    <p><strong>Summary:</strong> {escape(preview)}</p>
                    <h3>Key Points</h3>
                    <ul>
                        <li>The uploaded PDF was processed successfully.</li>
                        <li>If the file is image-based, OCR is not currently enabled in this build.</li>
                        <li>You can still email this fallback summary instead of receiving a server error.</li>
                    </ul>
                </div>
            </body>
        </html>
        """

async def summarize_document(text: str) -> str:
    """
    Summarizes the document text into HTML format using the configured LLM provider.
    """
    provider = settings.LLM_PROVIDER.lower()
    prompt = get_summarization_prompt(text)
    
    try:
        if not text.strip():
            return _fallback_html_summary(text)

        if provider == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment.")
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional assistant that generates HTML summaries of documents."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        elif provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment.")
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional assistant that generates HTML summaries of documents."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
            
    except Exception as e:
        logger.error(f"Error in AI summarization: {str(e)}")
        return _fallback_html_summary(text)
