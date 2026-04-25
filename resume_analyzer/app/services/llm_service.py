from typing import Dict, Any
import json
from openai import OpenAI
from app.core.config import settings
from app.schemas.resume import ResumeAnalysisResult

class LLMService:
    def __init__(self):
        base_url = None
        if settings.AI_PROVIDER == "groq":
            base_url = "https://api.groq.com/openai/v1"
        
        self.client = OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=base_url
        )

    def analyze_resume(self, resume_text: str) -> ResumeAnalysisResult:
        """Sends resume text to LLM and returns structured JSON analysis."""
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) and HR professional.
        Analyze the following resume text and provide a detailed extraction in JSON format.

        Resume Text:
        {resume_text}

        Your response MUST be a valid JSON object with the following structure:
        {{
            "name": "Full Name",
            "email": "Email Address",
            "skills": ["Skill 1", "Skill 2"],
            "experience": "Brief summary of experience",
            "education": "Brief summary of education",
            "ats_score": 85,
            "missing_skills": ["Missing Skill 1", "Missing Skill 2"],
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }}

        Ensure:
        - The ATS score is an integer between 0 and 100.
        - The missing_skills are relevant keywords for the candidate's career path.
        - The suggestions are actionable and specific.
        - ONLY return the JSON object. Do not include markdown code block markers or any other text.
        """

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional resume analyzer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" } if settings.AI_PROVIDER == "openai" or "llama3" in settings.AI_MODEL.lower() else None
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return ResumeAnalysisResult(**data)
        except Exception as e:
            # Fallback or re-raise
            print(f"LLM Error: {str(e)}")
            raise ValueError(f"AI Analysis failed: {str(e)}")

llm_service = LLMService()
