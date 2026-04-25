import google.generativeai as genai
from app.config.settings import settings

genai.configure(api_key=settings.gemini_api_key)

try:
    model = genai.GenerativeModel('gemini-pro-latest')
    response = model.generate_content("Say hello in JSON", generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
    print(response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
