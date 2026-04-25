import re

def get_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

import youtube_transcript_api

def fetch_youtube_transcript(url: str) -> str:
    """
    Fetches the transcript text for a given YouTube URL.
    """
    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    try:
        # Diagnostic: What does Python see?
        import youtube_transcript_api
        members = dir(youtube_transcript_api)
        
        # Method 1: The standard way
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            return " ".join([i['text'] for i in YouTubeTranscriptApi.get_transcript(video_id)])
        except (ImportError, AttributeError):
            pass
            
        # Method 2: The module way
        func = getattr(youtube_transcript_api, 'get_transcript', None)
        if not func:
            # Method 3: The class-via-module way
            cls = getattr(youtube_transcript_api, 'YouTubeTranscriptApi', None)
            func = getattr(cls, 'get_transcript', None)
            
        if not func:
            raise Exception(f"Library members found: {members}. No 'get_transcript' found.")
            
        transcript_list = func(video_id)
        return " ".join([i['text'] for i in transcript_list])

    except Exception as e:
        raise Exception(f"YouTube Library Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
