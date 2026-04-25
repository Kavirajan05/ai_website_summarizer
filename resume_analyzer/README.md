# Resume Analyzer AI Backend

A production-ready FastAPI backend that analyzes resumes (PDF/DOCX) using AI (Groq/OpenAI) and sends structured reports via email.

## 🚀 Features

- **File Upload**: Supports PDF and DOCX.
- **AI Analysis**: Extracts skills, experience, education, and generates an ATS score.
- **Email Reports**: Sends a clean HTML report directly to the provided email.
- **Async Processing**: Uses FastAPI `BackgroundTasks` for non-blocking analysis.
- **Validation**: Strict input validation using Pydantic.

## 🛠️ Setup

1. **Clone the repository** (or navigate to the folder).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Fill in your `AI_API_KEY` and SMTP credentials.
4. **Run the server**:
   ```bash
   python -m app.main
   ```
   Or using uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 API Endpoints

- `GET /health`: Health check.
- `POST /upload-resume`: Upload resume with `email` and `file`.

## 🐳 Docker Support

Build the image:
```bash
docker build -t resume-analyzer .
```
Run the container:
```bash
docker run -p 8000:8000 --env-file .env resume-analyzer
```
