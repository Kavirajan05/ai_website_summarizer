from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional

class SummarizeRequest(BaseModel):
    url: HttpUrl
    email: EmailStr

class SummaryReport(BaseModel):
    title: str
    summary: str
    insights: List[str]
    target_audience: str
    use_cases: List[str]
    features: List[str]
    keywords: List[str]
