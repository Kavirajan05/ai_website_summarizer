import re
import os
import yt_dlp
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_youtube_transcript(url: str) -> str:
    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    # STEP 1: Try the standard YouTube Transcript API (Fast & Free)
    try:
        ts = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            data = ts.find_transcript(['en']).fetch()
        except:
            try:
                data = ts.find_generated_transcript(['en']).fetch()
            except:
                data = next(iter(ts)).fetch()
        return " ".join([i['text'] for i in data])
    except Exception as e:
        print(f"Standard API Blocked: {str(e)}. Switching to Groq Whisper...")
        
        # STEP 2: FAILOVER - Use Groq Whisper (Speech-to-Text)
        return fetch_transcript_via_groq(url)

def fetch_transcript_via_groq(url: str) -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise Exception("Transcription blocked by Google. Please add GROQ_API_KEY to bypass this.")

    client = Groq(api_key=groq_key)
    audio_file = f"temp_audio_{get_video_id(url)}.m4a"
    
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': audio_file,
        'quiet': True,
        'no_warnings': True,
        # STEALTH SETTINGS (Force Android client to bypass bot check)
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'skip': ['hls', 'dash']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file, file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="en"
            )
        
        return transcription
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
