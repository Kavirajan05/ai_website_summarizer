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
        lib_path = getattr(yta, '__file__', 'unknown')

        # Deep Scan Logic
        def find_method(obj):
            for name in dir(obj):
                if name.endswith('Fetcher') or name.endswith('List') or name == 'YouTubeTranscriptApi':
                    continue
                if 'transcript' in name.lower() and ('get' in name.lower() or 'list' in name.lower()):
                    attr = getattr(obj, name)
                    if callable(attr) and not isinstance(attr, type):
                        return attr
            return None

        target = find_method(yta)
        if not target and hasattr(yta, 'YouTubeTranscriptApi'):
            # Try both class and instance
            target = find_method(yta.YouTubeTranscriptApi)
            if not target:
                target = find_method(yta.YouTubeTranscriptApi())

        if not target:
            raise Exception(f"Library path: {lib_path}. Members: {dir(yta)}. Maybe try installing 'pip install youtube-transcript-api' again.")

        result = target(video_id)
        # ... rest of the result handling logic ...
        
        # Handle different return types
        if isinstance(result, list):
            return " ".join([i['text'] for i in result])
        else:
            # Handle the result object from 'list_transcripts'
            try:
                # 1. Try manual English
                return " ".join([i['text'] for i in result.find_transcript(['en']).fetch()])
            except:
                try:
                    # 2. Try generated English
                    return " ".join([i['text'] for i in result.find_generated_transcript(['en']).fetch()])
                except:
                    # 3. Last resort: literally anything
                    return " ".join([i['text'] for i in next(iter(result)).fetch()])

    except Exception as e:
        raise Exception(f"Deep Scan Error: {str(e)}. Try visiting https://web-production-1c163c.up.railway.app/ to wake up the server.")

    except Exception as e:
        raise Exception(f"YouTube Nuclear Fix Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
