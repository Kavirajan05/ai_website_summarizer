import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

def _send_email_sync(to_email: str, subject: str, body: str):
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    
    if not email_user or not email_pass:
        logger.error("Email credentials are not set in environment variables.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, to_email, text)
        server.quit()
        logger.info(f"Email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

async def send_report_email(to_email: str, topic: str, report_body: str) -> bool:
    """
    Sends an email asynchronously so it doesn't block the FastAPI event loop.
    """
    subject = f"YouTube Learning Report – {topic}"
    return await asyncio.to_thread(_send_email_sync, to_email, subject, report_body)

