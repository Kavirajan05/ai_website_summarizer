import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, file_path):
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    email_from = os.getenv("EMAIL_FROM", email_user)
    email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    email_port = int(os.getenv("EMAIL_PORT", "587"))

    if not email_user or not email_pass:
        raise ValueError("Missing EMAIL_USER or EMAIL_PASS in .env")

    msg = EmailMessage()
    msg["Subject"] = "Your LinkedIn Profile Report"
    msg["From"] = email_from
    msg["To"] = to_email

    msg.set_content("Attached is your LinkedIn profile analysis report.")

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="report.pdf")

    with smtplib.SMTP(email_host, email_port) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)