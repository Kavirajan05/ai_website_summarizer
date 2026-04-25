from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class ResumeAnalysisResult(BaseModel):
    name: str = Field(..., description="Extract candidate name")
    email: str = Field(..., description="Extract candidate email")
    skills: List[str] = Field(..., description="List of technical and soft skills")
    experience: str = Field(..., description="Summary of work experience")
    education: str = Field(..., description="Summary of educational background")
    ats_score: int = Field(..., ge=0, le=100, description="ATS Score calculation")
    missing_skills: List[str] = Field(..., description="Skills typically expected for this profile but missing")
    suggestions: List[str] = Field(..., description="Actionable improvement suggestions")

class AnalysisResponse(BaseModel):
    message: str = "Resume analyzed and sent to email successfully"
