import httpx
import asyncio
import json

async def main():
    query = """
    [out:json][timeout:25];
    (
      nwr["name"~"plumber",i](around:5000,13.0827,80.2707);
    );
    out center;
    """
    try:
        r = httpx.post('https://overpass-api.de/api/interpreter', data=query, timeout=40.0)
        print("Status:", r.status_code)
        data = r.json()
        print("Elements found:", len(data.get("elements", [])))
        if data.get("elements"):
            print(json.dumps(data["elements"][0], indent=2))
        else:
            print("No elements")
    except Exception as e:
        print("Failed:", str(e))

asyncio.run(main())
