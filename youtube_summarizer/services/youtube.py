import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.
    """
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def fetch_transcript(video_id: str) -> str:
    """
    Fetches the transcript for a given YouTube video ID.
    """
    try:
        # Using the new instance-based API for version 1.2.4+
        transcript_data = YouTubeTranscriptApi().fetch(video_id)
        transcript_text = " ".join([snippet.text for snippet in transcript_data.snippets])
        return transcript_text
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
