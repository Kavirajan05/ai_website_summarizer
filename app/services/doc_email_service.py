import smtplib
from email.message import EmailMessage
from app.config.settings import settings

def send_doc_summary_email(recipient_email: str, doc_data: dict):
    """
    Sends the structured document summary to the user via email.
    """
    if not settings.smtp_user or not settings.smtp_pass:
        print("SMTP Credentials not configured. Skipping email delivery.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"AI Document Summary: {doc_data.get('title', 'Report')}"
    msg['From'] = settings.smtp_user
    msg['To'] = recipient_email

    # HTML Body Construction
    insights_html = "".join([f"<li>{i}</li>" for i in doc_data.get("insights", [])])
    keywords_html = ", ".join(doc_data.get("keywords", []))

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #e67e22; padding-bottom: 5px; }}
            h3 {{ color: #d35400; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; }}
            .summary {{ background-color: #fffaf0; padding: 15px; border-left: 4px solid #e67e22; margin-bottom: 20px; }}
            .keywords {{ font-style: italic; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 10px; margin-top: 20px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📄 Document Summary: {doc_data.get('title', 'Summary')}</h2>
            
            <div class="summary">
                <h3>Executive Summary</h3>
                <p>{doc_data.get('summary', 'No summary available.')}</p>
            </div>
            
            <h3>Key Insights & Takeaways</h3>
            <ul>
                {insights_html}
            </ul>
            
            <div class="keywords">
                <strong>Keywords:</strong> {keywords_html}
            </div>
            
            <p style="font-size: 0.8em; color: #bdc3c7; text-align: center; margin-top: 30px;">
                Generated automatically by AI Automation Hub - Document Summarizer.
            </p>
        </div>
    </body>
    </html>
    """

    msg.set_content("Please enable HTML to view this email properly.")
    msg.add_alternative(html_content, subtype='html')

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                server.login(settings.smtp_user, settings.smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_pass)
                server.send_message(msg)
        print(f"Document summary email successfully sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send document summary email to {recipient_email}: {e}")
