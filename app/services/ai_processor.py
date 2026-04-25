import json
import google.generativeai as genai
from app.config.settings import settings

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def process_with_ai(scraped_text: str) -> dict:
    """
    Sends the scraped text to the LLM and asks for structured JSON output.
    """
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

    model = genai.GenerativeModel('gemini-flash-latest')
    
    # We can use generation_config to ensure JSON output
    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )
    
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    
    try:
        # Load the text as JSON
        result = json.loads(response.text)
        return result
    except json.JSONDecodeError:
        raise Exception("LLM did not return a valid JSON format.")
