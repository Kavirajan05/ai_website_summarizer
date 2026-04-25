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
        # Auto-discover models to avoid 404 Errors
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models:
            raise Exception("No generative models found for this API key.")
        
        # Pick the best model (prefer flash-1.5, then flash, then anything else)
        model_name = "models/gemini-1.5-flash" # Default guess
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        else:
            model_name = available_models[0]

        model = genai.GenerativeModel(model_name)
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
