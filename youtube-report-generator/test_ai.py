import asyncio
from dotenv import load_dotenv
import logging
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

from services.ai import rank_videos

async def test():
    videos = [
        {"title": "Test Video 1", "channel": "Test Channel 1", "videoId": "123", "url": "http://test"}
    ]
    res = await rank_videos(videos)
    print("RESULT:", res)

asyncio.run(test())
