import smtplib
from email.message import EmailMessage
from app.config.settings import settings

def send_summary_email(recipient_email: str, target_url: str, report: dict):
    """
    Sends the structured summary report to the user via email.
    """
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_pass:
        raise ValueError("SMTP configuration is incomplete.")

    msg = EmailMessage()
    msg['Subject'] = f"AI Website Summary: {report.get('title', 'Report')}"
    msg['From'] = settings.smtp_user
    msg['To'] = recipient_email

    # HTML Body Construction
    insights_html = "".join([f"<li>{i}</li>" for i in report.get("insights", [])])
    use_cases_html = "".join([f"<li>{u}</li>" for u in report.get("use_cases", [])])
    features_html = "".join([f"<li>{f}</li>" for f in report.get("features", [])])
    keywords_html = ", ".join(report.get("keywords", []))

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            h3 {{ color: #2980b9; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .summary {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #3498db; }}
            .keywords {{ font-style: italic; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Website Summary: {report.get('title', 'Unknown Title')}</h2>
            <p><strong>Source URL:</strong> <a href="{target_url}">{target_url}</a></p>
            
            <h3>Summary</h3>
            <div class="summary">
                <p>{report.get('summary', 'No summary available.')}</p>
            </div>
            
            <h3>Target Audience</h3>
            <p>{report.get('target_audience', 'Not specified.')}</p>
            
            <h3>Key Insights</h3>
            <ul>
                {insights_html}
            </ul>
            
            <h3>Use Cases</h3>
            <ul>
                {use_cases_html}
            </ul>
            
            <h3>Key Features / Services</h3>
            <ul>
                {features_html}
            </ul>
            
            <h3>Keywords</h3>
            <p class="keywords">{keywords_html}</p>
        </div>
    </body>
    </html>
    """


    msg.set_content("Please enable HTML to view this email.")
    msg.add_alternative(html_content, subtype='html')

    try:
        # Use SMTP_SSL for port 465, otherwise use standard SMTP with STARTTLS
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                server.login(settings.smtp_user, settings.smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_pass)
                server.send_message(msg)
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
