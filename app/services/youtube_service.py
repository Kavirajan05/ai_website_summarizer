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
        # Extra safe way to call the transcript function
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        except AttributeError:
            # Fallback for different library versions
            import youtube_transcript_api
            func = getattr(youtube_transcript_api, 'get_transcript', None)
            if not func:
                # Last resort: search inside the class
                cls = getattr(youtube_transcript_api, 'YouTubeTranscriptApi', None)
                func = getattr(cls, 'get_transcript', None)
            
            if not func:
                raise Exception("Could not find 'get_transcript' in the library.")
                
            transcript_list = func(video_id)

        transcript_text = " ".join([i['text'] for i in transcript_list])
        return transcript_text
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
