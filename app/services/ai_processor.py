import json
import google.generativeai as genai
from app.config.settings import settings

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def process_with_ai(scraped_text: str) -> dict:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    
    prompt = f"""
    Analyze the following website content and generate exactly:
    1. A concise summary
    2. Key insights
    3. Target audience
    4. Use cases
    5. Key features/services
    6. Important keywords
    
    You MUST format your output strictly as a JSON object, exactly like this:
    {{
      "title": "Title of the page/site",
      "summary": "5-7 lines concise overview",
      "insights": ["insight 1", "insight 2"],
      "target_audience": "Who this website is for",
      "use_cases": ["use case 1", "use case 2"],
      "features": ["feature 1", "feature 2"],
      "keywords": ["keyword1", "keyword2"]
    }}
    
    Content:
    {scraped_text}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        raise Exception(f"Google AI Error: {str(e)}")

def main_generation_config():
    return genai.types.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.2,
    )
