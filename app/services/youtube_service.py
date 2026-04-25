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
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Method: List all transcripts then pick one
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find English, then fall back to any available
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            # If English is not found, take the first one available
            transcript = next(iter(transcript_list))

        data = transcript.fetch()
        return " ".join([i['text'] for i in data])

    except Exception as e:
        raise Exception(f"YouTube Transcript Tool Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
