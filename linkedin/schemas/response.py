from pydantic import BaseModel
from typing import List

class AnalyzeResponse(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    improved_headline: str
    improved_about: str