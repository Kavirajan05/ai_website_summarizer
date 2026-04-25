from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
import re

class SummarizeRequest(BaseModel):
    email: EmailStr
    youtube_url: HttpUrl

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, v: HttpUrl) -> HttpUrl:
        url = str(v)
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        if not re.match(youtube_regex, url):
            raise ValueError("Invalid YouTube URL format")
        return v
