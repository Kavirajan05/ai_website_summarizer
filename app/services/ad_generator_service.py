import os
import base64
from io import BytesIO
import logging
from PIL import Image
from groq import Groq
from huggingface_hub import InferenceClient
from app.config.settings import settings

logger = logging.getLogger(__name__)

def generate_ad_prompt(product_title: str, product_description: str) -> str:
    """Generates a high-quality marketing prompt using Groq."""
    try:
        if not settings.groq_api_key:
            return f"Hyper-realistic professional studio photography of {product_title}, {product_description}, clean minimalistic elegant style, softbox lighting, high detail, realistic textures, smooth white background, premium advertising look"

        client = Groq(api_key=settings.groq_api_key)
        
        system_prompt = """You are a world-class marketing strategist and an expert text-to-image prompt engineer specializing in creating hyper-realistic, high-quality product photography prompts for AI image generation models.

Your Objective:
When given a product description, craft a detailed, professional prompt that results in a hyper-realistic, clean, and visually stunning product image suitable for marketing, advertising, or e-commerce.

Requirements:
- Hyper-realistic professional studio photography
- Clean, minimalistic, elegant style
- Product centered and clearly visible
- Softbox lighting or natural soft shadows
- High detail, realistic textures
- Smooth clean background (white or gradient)
- Premium, high-end advertising look

Output:
Return ONLY the final prompt. No explanation."""
        
        user_input = f"Product: {product_title}\nDescription: {product_description}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192",
        )
        
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq prompt generation failed: {e}")
        return f"Professional studio photography of {product_title}, {product_description}, high quality marketing shot"

def generate_marketing_image(input_image_bytes: bytes, product_title: str, product_description: str) -> str:
    """Generates an enhanced marketing image and returns as base64 string."""
    try:
        # Step 1: Generate the prompt
        marketing_prompt = generate_ad_prompt(product_title, product_description)
        logger.info(f"Generated prompt: {marketing_prompt}")
        
        if not settings.hf_token:
            raise ValueError("Hugging Face token (HF_TOKEN) is not configured.")

        # Step 2: Initialize HF Client
        hf_client = InferenceClient(
            provider="fal-ai",
            api_key=settings.hf_token,
        )
        
        # Step 3: Run image-to-image generation
        # We pass bytes directly to HF client
        generated_image = hf_client.image_to_image(
            input_image_bytes,
            prompt=marketing_prompt,
            model="black-forest-labs/FLUX.2-dev",
            strength=0.4,
            guidance_scale=7.5
        )
        
        # Step 4: Convert PIL image to base64
        buffered = BytesIO()
        generated_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise ValueError(f"Failed to generate marketing image: {str(e)}")
