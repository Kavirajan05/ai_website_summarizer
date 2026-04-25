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
        import youtube_transcript_api as yta
        
        # Aggressive Search: Try to find the function anywhere in the library
        target_func = None
        
        # Choice 1: Check the class
        if hasattr(yta, 'YouTubeTranscriptApi'):
            cls = yta.YouTubeTranscriptApi
            for name in ['get_transcript', 'list_transcripts']:
                if hasattr(cls, name):
                    target_func = getattr(cls, name)
                    break
        
        # Choice 2: Check the module directly
        if not target_func:
            for name in ['get_transcript', 'list_transcripts']:
                if hasattr(yta, name):
                    target_func = getattr(yta, name)
                    break

        if not target_func:
            # Final attempt: direct import from the inner module
            try:
                from youtube_transcript_api._transcripts import YouTubeTranscriptApi as DirectClass
                target_func = DirectClass.get_transcript
            except:
                raise Exception(f"Fatal: Could not find YouTube function in library members: {dir(yta)}")

        # Execute
        result = target_func(video_id)
        
        # Parse result (it could be a list or a Transcripts object)
        if hasattr(result, 'find_transcript'):
            # It's a Transcripts object (from list_transcripts)
            try:
                final_data = result.find_transcript(['en']).fetch()
            except:
                final_data = next(iter(result)).fetch()
        else:
            # It's a list (from get_transcript)
            final_data = result

        return " ".join([i['text'] for i in final_data])

    except Exception as e:
        raise Exception(f"YouTube Nuclear Fix Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
