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
        
        # Deep Scan Logic: Find the REAL function and skip all classes
        def find_method(obj):
            # Prioritize 'get_transcript' specifically
            if hasattr(obj, 'get_transcript'):
                return getattr(obj, 'get_transcript')
            
            for name in dir(obj):
                # Skip any names that look like classes (start with capital or end in Fetcher/List)
                if name.endswith('Fetcher') or name.endswith('List') or name == 'YouTubeTranscriptApi':
                    continue
                    
                if 'transcript' in name.lower() and ('get' in name.lower() or 'list' in name.lower()):
                    attr = getattr(obj, name)
                    # ONLY pick it if it's a function, NOT a class (type)
                    if callable(attr) and not isinstance(attr, type):
                        return attr
            return None

        # 1. Look in the module
        target = find_method(yta)
        
        # 2. Look in the main class
        if not target and hasattr(yta, 'YouTubeTranscriptApi'):
            target = find_method(yta.YouTubeTranscriptApi)
            
        # 3. Look in the inner api module
        if not target and hasattr(yta, '_api'):
            target = find_method(yta._api)

        if not target:
            # Absolute last resort: try to force it
            from youtube_transcript_api import YouTubeTranscriptApi
            target = YouTubeTranscriptApi.get_transcript

        result = target(video_id)
        
        # Handle different return types
        if isinstance(result, list):
            return " ".join([i['text'] for i in result])
        else:
            # Assume it's a Transcripts object
            try:
                return " ".join([i['text'] for i in result.find_transcript(['en']).fetch()])
            except:
                return " ".join([i['text'] for i in next(iter(result)).fetch()])

    except Exception as e:
        raise Exception(f"Deep Scan Error: {str(e)}. Try visiting https://web-production-1c163c.up.railway.app/ to wake up the server.")

    except Exception as e:
        raise Exception(f"YouTube Nuclear Fix Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {str(e)}")
