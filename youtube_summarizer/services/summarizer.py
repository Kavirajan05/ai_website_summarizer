import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(transcript: str) -> str:
    """
    Generates a summary of the transcript using Groq.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise Exception("Groq API key not found in environment variables.")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube videos into clear bullet points and a short explanation."},
                {"role": "user", "content": transcript[:12000]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"AI summarization failed: {str(e)}")
