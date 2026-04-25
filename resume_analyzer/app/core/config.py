from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, EmailStr

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Resume Analyzer AI"
    DEBUG: bool = False
    
    # AI Configuration
    AI_PROVIDER: Literal["openai", "groq"] = "groq"
    AI_API_KEY: str
    AI_MODEL: str = "llama3-8b-8192"
    
    # Email Configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASS: str
    EMAIL_FROM: EmailStr
    
    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
