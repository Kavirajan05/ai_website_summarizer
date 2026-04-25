import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_transcript(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)

        transcript_text = " ".join(
            [snippet.text for snippet in transcript_data.snippets]
        )

        return transcript_text.strip()

    except Exception as e:
        raise Exception(f"Could not fetch transcript: {e}")