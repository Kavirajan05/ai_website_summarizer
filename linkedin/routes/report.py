from fastapi import APIRouter
from services.report import generate_pdf

router = APIRouter()

@router.post("/generate-report")
def report(data: dict):
    path = generate_pdf(data)
    return {"pdf": path}