import os
import base64
from io import BytesIO
import logging
from PIL import Image
import google.generativeai as genai
from groq import Groq
from huggingface_hub import InferenceClient
from app.config.settings import settings

logger = logging.getLogger(__name__)

def describe_image_with_vision(image_bytes: bytes) -> str:
    """Uses Gemini Vision to describe the product in detail."""
    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Convert bytes to PIL for Gemini
        img = Image.open(BytesIO(image_bytes))
        
        response = model.generate_content([
            "Describe this product in extreme detail for a professional photographer. "
            "Mention its color, texture, material, shape, and unique features. "
            "Focus only on the product itself, not the background.",
            img
        ])
        return response.text.strip()
    except Exception as e:
        logger.error(f"Vision description failed: {e}")
        return "A professional product"

def generate_ad_prompt(product_title: str, product_description: str, vision_details: str) -> str:
    """Generates a high-quality marketing prompt using Groq or Gemini."""
    system_prompt = """You are a world-class marketing strategist and an expert text-to-image prompt engineer.
Your Objective: Create a detailed, professional prompt for a hyper-realistic, high-end studio product photograph.
Requirements:
- Hyper-realistic professional studio photography
- Clean, minimalistic, elegant style
- Product centered and clearly visible
- Softbox lighting, high detail, realistic textures
- Smooth clean background (white or gradient)
- Premium, high-end advertising look
Output: Return ONLY the final prompt. No explanation."""

    user_input = f"Product: {product_title}\nDescription: {product_description}\nVisual Details: {vision_details}"
    
    try:
        if settings.groq_api_key:
            client = Groq(api_key=settings.groq_api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content.strip()
    except Exception:
        pass

    # Fallback to Gemini
    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(f"{system_prompt}\n\n{user_input}")
        return response.text.strip()
    except Exception:
        return f"Hyper-realistic professional studio photography of {product_title}, {product_description}, premium advertising look"

def generate_marketing_image(input_image_bytes: bytes, product_title: str, product_description: str) -> str:
    """Generates a professional marketing ad using Vision + FLUX."""
    try:
        # Step 1: Use Vision to "see" the product
        vision_details = describe_image_with_vision(input_image_bytes)
        logger.info(f"Vision details: {vision_details}")
        
        # Step 2: Generate the perfect studio prompt
        marketing_prompt = generate_ad_prompt(product_title, product_description, vision_details)
        logger.info(f"Final Prompt: {marketing_prompt}")
        
        if not settings.hf_token:
            raise ValueError("Hugging Face token (HF_TOKEN) is not configured.")

        # Step 3: Initialize HF Client (Native)
        hf_client = InferenceClient(api_key=settings.hf_token)
        
        # Step 4: Use FLUX Text-to-Image (More reliable than image-to-image)
        # This will create a fresh, professional version of your product
        generated_image = hf_client.text_to_image(
            marketing_prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )
        
        # Step 5: Convert PIL image to base64
        buffered = BytesIO()
        generated_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise ValueError(f"Failed to generate marketing image: {str(e)}")
