import httpx
import asyncio
import json

async def main():
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "plumber in chennai",
        "format": "json",
        "limit": 10
    }
    headers = {"User-Agent": "LocalServiceFinder/1.0"}
    r = httpx.get(url, params=params, headers=headers)
    print(r.status_code)
    try:
        data = r.json()
        print(f"Found {len(data)} results in Nominatim.")
        if data:
            print(json.dumps(data[0], indent=2))
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
