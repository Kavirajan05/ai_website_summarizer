from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.core.config import settings
from app.schemas.resume import ResumeAnalysisResult
from typing import Dict

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USER,
    MAIL_PASSWORD=settings.EMAIL_PASS,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailService:
    def __init__(self):
        self.fastmail = FastMail(conf)

    async def send_analysis_report(self, recipient_email: str, result: ResumeAnalysisResult):
        """Sends a clean HTML report of the resume analysis."""
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; text-align: center;">Resume Analysis Report</h2>
                    <hr>
                    <p><strong>Name:</strong> {result.name}</p>
                    <p><strong>ATS Score:</strong> <span style="font-size: 20px; color: {'#27ae60' if result.ats_score > 70 else '#e67e22'}; font-weight: bold;">{result.ats_score}/100</span></p>
                    
                    <h3>Skills Extracted</h3>
                    <ul style="column-count: 2;">
                        {''.join(f'<li>{skill}</li>' for skill in result.skills)}
                    </ul>
                    
                    <h3>Experience Summary</h3>
                    <p>{result.experience}</p>
                    
                    <h3>Education</h3>
                    <p>{result.education}</p>
                    
                    <h3>Missing Keywords/Skills</h3>
                    <p style="color: #c0392b;">{', '.join(result.missing_skills)}</p>
                    
                    <h3>Improvement Suggestions</h3>
                    <ul>
                        {''.join(f'<li>{s}</li>' for s in result.suggestions)}
                    </ul>
                    
                    <hr>
                    <p style="font-size: 12px; color: #7f8c8d; text-align: center;">Sent via Resume Analyzer AI</p>
                </div>
            </body>
        </html>
        """

        message = MessageSchema(
            subject=f"Resume Analysis Report for {result.name}",
            recipients=[recipient_email],
            body=html,
            subtype=MessageType.html
        )

        try:
            await self.fastmail.send_message(message)
        except Exception as e:
            print(f"Email Error: {str(e)}")
            raise ValueError(f"Failed to send email: {str(e)}")

email_service = EmailService()
