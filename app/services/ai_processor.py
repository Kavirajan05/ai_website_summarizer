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

    # Using gemini-1.5-flash-latest for better compatibility
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(
            prompt,
            generation_config=main_generation_config()
        )
    except Exception as e:
        if "404" in str(e):
            # Fallback to gemini-pro if Flash is not found
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
        else:
            raise e
    
    raw_text = response.text.strip()
    
    # Robust JSON extraction
    try:
        # 1. Try direct parse
        return json.loads(raw_text)
    except json.JSONDecodeError:
        try:
            # 2. Try cleaning markdown markers if present
            clean_text = raw_text
            if "```" in raw_text:
                clean_text = raw_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            return json.loads(clean_text)
        except Exception:
            # 3. Last resort: just try to find the first { and last }
            try:
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                if start != -1 and end != 0:
                    return json.loads(raw_text[start:end])
                else:
                    raise Exception("No JSON object found in response.")
            except Exception:
                raise Exception(f"AI returned invalid format. Raw: {raw_text[:100]}...")

def main_generation_config():
    return genai.types.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.2,
    )
