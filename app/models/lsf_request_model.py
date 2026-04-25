from pydantic import BaseModel, EmailStr

class ServiceRequest(BaseModel):
    service: str
    city: str
    email: EmailStr
