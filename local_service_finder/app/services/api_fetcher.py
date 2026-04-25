import httpx
from app.config.settings import settings

async def fetch_serpapi_services(service: str, city: str) -> list:
    if not settings.SERPAPI_KEY:
        print("SERPAPI_KEY is missing in settings.")
        return []

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_local",
        "q": f"{service} in {city}",
        "location": city,
        "api_key": settings.SERPAPI_KEY
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=20.0)
            response.raise_for_status()
            data = response.json()
            
            local_results = data.get("local_results", [])
            
            # SerpAPI response format can vary:
            # 1. local_results is a list of places
            # 2. local_results is a dict with a "places" key
            if isinstance(local_results, dict):
                places = local_results.get("places", [])
            else:
                places = local_results

            formatted_places = []
            
            for place in places:
                # SerpAPI uses 'title' for business name
                gps = place.get("gps_coordinates", {})
                
                formatted_places.append({
                    "name": place.get("title", "Unknown"),
                    "address": place.get("address", place.get("address_extended", "N/A")),
                    "rating": place.get("rating", 0),
                    "reviews_count": place.get("reviews", 0),
                    "phone": place.get("phone", "N/A"),
                    "website": place.get("website", "N/A"),
                    "lat": gps.get("latitude"),
                    "lon": gps.get("longitude"),
                    "type": place.get("type", "Service")
                })
                
            return formatted_places
        except httpx.HTTPError as e:
            print(f"Error fetching data from SerpAPI: {e}")
            # If it's a 401/403, it might be an invalid key
            if hasattr(e, 'response') and e.response:
                print(f"Response Detail: {e.response.text}")
            return []
