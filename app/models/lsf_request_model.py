from pydantic import BaseModel, EmailStr
from typing import Optional

class ServiceRequest(BaseModel):
    service: str
    city: str
    email: Optional[EmailStr] = None
