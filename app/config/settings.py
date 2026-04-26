from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    groq_api_key: str = ""
    openai_api_key: str = ""
    serpapi_key: str = ""
    google_places_api_key: str = ""
    email_api_key: str = ""
    youtube_api_key: str = ""
    hf_token: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
