from fastapi import APIRouter
from services.email import send_email

router = APIRouter()

@router.post("/send-email")
def email(data: dict):
    send_email(data["email"], data["file"])
    return {"status": "Email sent"}