from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_PLACES_API_KEY: str = ""
    SERPAPI_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    EMAIL_API_KEY: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
