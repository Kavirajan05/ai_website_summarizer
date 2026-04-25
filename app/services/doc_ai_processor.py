import json
import google.generativeai as genai
from app.config.settings import settings

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def summarize_document_with_ai(text: str) -> dict:
    """
    Summarizes document text using Google Gemini 1.5 Flash.
    Returns a structured JSON object.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    
    if not text.strip():
        return {
            "title": "Empty Document",
            "summary": "The document contains no extractable text.",
            "insights": [],
            "keywords": []
        }

    prompt = f"""
    Analyze the following document text and generate a structured summary.
    
    Tasks:
    1. Provide a professional title for the document.
    2. Write a concise but comprehensive summary (5-10 lines).
    3. List 5-7 key insights or main points.
    4. Provide 5-8 relevant keywords.
    
    You MUST format your output strictly as a JSON object, exactly like this:
    {{
      "title": "...",
      "summary": "...",
      "insights": ["...", "..."],
      "keywords": ["...", "..."]
    }}
    
    Document Content:
    {text[:20000]}  # Truncate to stay within context limits if necessary
    """

    try:
        # Auto-discover models to avoid 404 Errors
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Pick the best model
        model_name = "gemini-1.5-flash" # Default
        if "models/gemini-1.5-flash" in available_models:
            model_name = "models/gemini-1.5-flash"
        elif any("flash" in m for m in available_models):
            model_name = next(m for m in available_models if "flash" in m)
        elif available_models:
            model_name = available_models[0]

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        text_resp = response.text.strip()
        
        # Clean Markdown if needed
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[-1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[-1].split("```")[0].strip()
            
        return json.loads(text_resp)
        
    except Exception as e:
        print(f"Document AI Analysis failed: {str(e)}")
        # Fallback
        return {
            "title": "Document Summary",
            "summary": "An error occurred during AI analysis. Here is the raw text preview: " + text[:200] + "...",
            "insights": ["AI analysis failed."],
            "keywords": ["error"]
        }
