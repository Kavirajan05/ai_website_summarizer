import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)

async def send_html_email(to_email: str, subject: str, html_content: str):
    """
    Sends an HTML email using the configured SMTP settings.
    """
    if not all([settings.SMTP_USER, settings.SMTP_PASS]):
        logger.warning("SMTP credentials not configured. Skipping email sending.")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Email successfully sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise Exception(f"Email sending failed: {str(e)}")
