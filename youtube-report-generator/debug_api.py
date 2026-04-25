import asyncio
import os
from dotenv import load_dotenv
import logging
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test_search():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("API_KEY IS MISSING FROM ENV")
        return
        
    print(f"API key loaded: {api_key[:5]}... (length: {len(api_key)})")
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "q": "AI agent",
        "type": "video",
        "maxResults": 4,
        "part": "snippet"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

asyncio.run(test_search())
