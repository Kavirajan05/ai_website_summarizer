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
        # Using the standard static method call
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Get the list object which is much more reliable
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # 1. Manual English
            data = transcript_list.find_transcript(['en']).fetch()
        except:
            try:
                # 2. Generated English
                data = transcript_list.find_generated_transcript(['en']).fetch()
            except:
                # 3. Anything else
                data = next(iter(transcript_list)).fetch()

        return " ".join([snippet['text'] for snippet in data]).strip()

    except Exception as e:
        raise Exception(f"Could not fetch transcript: {e}")