import json
import google.generativeai as genai
from app.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

async def analyze_services_with_ai(service: str, city: str, formatted_places: list) -> dict:
    if not formatted_places:
        return {
            "service": service,
            "city": city,
            "top_recommendations": [],
            "best_choice": {},
            "summary": "No services found matching the criteria.",
            "insights": []
        }
        
    # Using the latest stable model string
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
Analyze the following list of local {service} providers in {city} fetched from Google Local data.

Tasks:
1. Recommend the top 5 providers based on their ratings, number of reviews, and overall service credibility.
2. Select the absolute "Best Choice" and provide a detailed explanation.
3. Provide a summary of the service landscape in {city}.
4. List key insights (e.g., price ranges if available, density of services, high-rated areas).
5. Calculate a "Trust Score" (0-100) for the best option.

Return ONLY a valid JSON object with the following structure:
{{
  "service": "{service}",
  "city": "{city}",
  "top_recommendations": [
     {{
        "name": "...",
        "rating": 0,
        "reviews_count": 0,
        "reasoning": "...",
        "phone": "...",
        "website": "...",
        "lat": "...",
        "lon": "..."
     }}
  ],
  "best_choice": {{
     "name": "...",
     "reasoning": "...",
     "trust_score": 0,
     "lat": "...",
     "lon": "..."
  }},
  "summary": "...",
  "insights": ["...", "..."]
}}

Data:
{json.dumps(formatted_places, indent=2)}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up Markdown formatting if any
        if "```json" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[-1].split("```")[0].strip()
        
        result = json.loads(text.strip())
        return result
    except Exception as e:
        print(f"AI Analysis failed critically: {str(e)}")
        # Fallback to structured results but without AI analysis
        return {
            "service": service,
            "city": city,
            "top_recommendations": formatted_places[:5],
            "best_choice": formatted_places[0] if formatted_places else {},
            "summary": f"Automated summary: Found {len(formatted_places)} results for {service} in {city}. Higher rated providers are listed first.",
            "insights": ["Ratings and reviews were used to sort the providers."]
        }
