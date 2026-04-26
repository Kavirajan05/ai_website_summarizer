from pydantic import BaseModel, EmailStr

class AnalyzeRequest(BaseModel):
    url: str
    email: EmailStr