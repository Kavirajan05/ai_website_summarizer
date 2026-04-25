# AI Website Summarizer

A fully automated AI workflow that takes a website URL as input, extracts its content, analyzes it using an LLM (Gemini), and sends a structured summary report via email.

## Setup Instructions

1. Clone the repository and navigate to the project root.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure the `.env` file with your `GEMINI_API_KEY` and your `SMTP` credentials (e.g., standard Gmail SMTP settings with an App Password).
6. Run the application: `uvicorn app.main:app --reload`
7. The API will be available at `http://127.0.0.1:5001`.

## API Documentation

- **POST /summarize-website**

**Request:**
```json
{
  "url": "https://example.com",
  "email": "user@email.com"
}
```

**Response:**
```json
{
  "status": "processing",
  "message": "Report will be sent to email"
}
```
