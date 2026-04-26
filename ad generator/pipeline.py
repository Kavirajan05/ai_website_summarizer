import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# Initialize API clients
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

hf_client = InferenceClient(
    provider="fal-ai",
    api_key=os.environ.get("HF_TOKEN"),
)

def generate_prompt(product_title: str, product_description: str) -> str:
    """Generates a high-quality marketing prompt using Groq."""
    
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
Return ONLY the final prompt. No explanation.
"""
    
    user_input = f"Product: {product_title}\nDescription: {product_description}"
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="llama3-8b-8192",  # Standard Groq model, can be updated if needed
    )
    
    return chat_completion.choices[0].message.content.strip()

def generate_image(input_image_path: str, marketing_prompt: str, output_path: str = "output.png"):
    """Generates an enhanced image using Hugging Face (fal-ai) and saves it."""
    
    # Hugging Face inference client's image_to_image takes a file-like object, bytes, or file path.
    # The SDK supports paths or PIL images natively.
    image = hf_client.image_to_image(
        input_image_path,
        prompt=marketing_prompt,
        model="black-forest-labs/FLUX.2-dev",
        strength=0.4,
        guidance_scale=7.5
    )
    
    # Save the returned PIL image to file
    image.save(output_path)

def send_email_with_attachment(recipient_email: str, attachment_path: str):
    """Sends an email with the generated image as an attachment."""
    
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    sender_email = os.environ.get("SENDER_EMAIL", smtp_user)
    
    msg = EmailMessage()
    msg["Subject"] = "Your AI Generated Marketing Image"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content("Here is your professionally generated marketing image.")
    
    # Attach image
    with open(attachment_path, "rb") as f:
        img_data = f.read()
        
    msg.add_attachment(img_data, maintype="image", subtype="png", filename=os.path.basename(attachment_path))
    
    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

def run_pipeline(product_image_path: str, product_title: str, product_description: str, email: str):
    """Runs the full marketing ad generation pipeline."""
    try:
        # Step 1: Generate Prompt
        marketing_prompt = generate_prompt(product_title, product_description)
        
        # Step 2 & 3: Generate Image & Save
        generate_image(product_image_path, marketing_prompt, "output.png")
        print("Image generated successfully")
        
        # Step 4: Send Email
        send_email_with_attachment(email, "output.png")
        print("Email sent successfully")
        
        # Return exact strings as requested
        return ["Image generated successfully", "Email sent successfully"]
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Marketing Image Generator Pipeline")
    parser.add_argument("--image", required=True, help="Path to the input product image")
    parser.add_argument("--title", required=True, help="Product title")
    parser.add_argument("--desc", required=True, help="Product description")
    parser.add_argument("--email", required=True, help="Recipient email address")

    args = parser.parse_args()

    run_pipeline(args.image, args.title, args.desc, args.email)
