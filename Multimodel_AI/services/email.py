"""
services/email.py — Async SMTP email sender using aiosmtplib
"""

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
from loguru import logger

EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


async def send_html_email(to_address: str, subject: str, html_body: str) -> None:
    """
    Send an HTML email via Gmail SMTP using aiosmtplib (fully async).

    Args:
        to_address: Recipient email address.
        subject:    Email subject line.
        html_body:  Fully rendered HTML content.

    Raises:
        ValueError: If EMAIL_USER or EMAIL_PASS are not configured.
        aiosmtplib.SMTPException: On SMTP transmission failure.
    """
    if not EMAIL_USER or not EMAIL_PASS:
        raise ValueError("EMAIL_USER and EMAIL_PASS must be set in .env")

    # Build MIME message
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_USER
    message["To"] = to_address
    message["Subject"] = subject

    # Attach plain-text fallback + HTML part
    plain_fallback = "Please view this email in an HTML-capable client."
    message.attach(MIMEText(plain_fallback, "plain"))
    message.attach(MIMEText(html_body, "html"))

    logger.info(f"[Email] Sending to {to_address!r} | subject={subject!r}")

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=EMAIL_USER,
        password=EMAIL_PASS,
        start_tls=True,
    )

    logger.info(f"[Email] Successfully delivered to {to_address!r}")
