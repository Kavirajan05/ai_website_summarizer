from fastapi import APIRouter
from schemas.request import AnalyzeRequest
from services.linkedin import fetch_profile_text
from services.groq_service import analyze_with_groq
from services.report import generate_pdf
from services.email import send_email

router = APIRouter()

@router.post("/analyze")
def analyze_profile(data: AnalyzeRequest):
    profile_text = fetch_profile_text(data.url)

    result = analyze_with_groq(profile_text)
    result["message"] = result.get("message") or "Try this: use the suggestions in the dashboard report to improve your headline and about section."

    pdf_path = generate_pdf(result)

    send_email(data.email, pdf_path)

    return {
        "message": "Analysis completed. Try this: open the dashboard report and apply the top suggestions.",
        "report_path": pdf_path,
        "data": result
    }