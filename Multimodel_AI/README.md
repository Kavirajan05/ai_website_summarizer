# 🤖 Multi-Model AI Summarization API

A production-ready FastAPI backend that queries **OpenRouter (Qwen)**, **Groq (LLaMA 3.3 70B)**, and **Google Gemini** in parallel, aggregates their responses, summarizes them into a structured report, and delivers it as a formatted HTML email.

---

## 📁 Project Structure

```
Multimodel_AI/
├── main.py                  # FastAPI app & routes
├── services/
│   ├── llm.py               # Async LLM calls (OpenRouter, Groq, Gemini)
│   ├── summarizer.py        # Final summarization via OpenRouter
│   └── email.py             # Async SMTP email sender
├── utils/
│   ├── formatter.py         # Plain-text → HTML converter
│   └── logger.py            # Loguru logging setup
├── .env                     # API keys & config (never commit this!)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Create & activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Edit `.env` and fill in your keys:

```env
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
```

> **Gmail note:** Use an [App Password](https://myaccount.google.com/apppasswords), not your regular Gmail password. Enable 2FA first.

### 4. Run the server

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔌 API Reference

### `POST /summarize` — Async (background task)

Kicks off the pipeline in the background and returns immediately.

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the applications of quantum computing", "email": "you@example.com"}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Your AI summary is being generated and will be sent to you@example.com shortly."
}
```

---

### `POST /summarize/sync` — Synchronous

Waits for the full pipeline before responding. Ideal for testing.

```bash
curl -X POST http://localhost:8000/summarize/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "What is blockchain?", "email": "you@example.com"}'
```

---

### `GET /health`

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

### Interactive Docs

Visit **http://localhost:8000/docs** for the auto-generated Swagger UI.

---

## 🔄 Pipeline Flow

```
POST /summarize
      │
      ▼
┌─────────────────────────────────────┐
│  Parallel LLM calls (asyncio.gather)│
│  ├── OpenRouter (Qwen)              │
│  ├── Groq (LLaMA 3.3 70B)          │
│  └── Google Gemini                  │
└────────────────┬────────────────────┘
                 │
                 ▼
         Merge all responses
                 │
                 ▼
    Final summarization (OpenRouter)
    → Title, Overview, Key Points,
      Strengths, Challenges, Conclusion
                 │
                 ▼
       Convert to HTML (formatter)
                 │
                 ▼
      Send HTML email via SMTP
```

---

## 🔐 Security

- All secrets are loaded from `.env` (never hardcoded)
- Rate limiting: `10 requests/minute` per IP (configurable via `RATE_LIMIT_PER_MINUTE`)
- Input validation: query length capped at 2000 characters
- Global error handler prevents stack traces leaking to clients

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `httpx` | Async HTTP client |
| `google-generativeai` | Gemini SDK |
| `aiosmtplib` | Async SMTP |
| `tenacity` | Retry logic |
| `slowapi` | Rate limiting |
| `loguru` | Structured logging |
| `python-dotenv` | `.env` loading |

---

## 🚀 Bonus Features Included

- ✅ Retry mechanism (3 attempts, exponential back-off) on LLM calls
- ✅ Per-provider graceful error capture (one failure doesn't break the pipeline)
- ✅ Response ranking utility (`rank_responses()` in `services/llm.py`)
- ✅ Rotating log files in `logs/app.log`
- ✅ Both async (background) and sync endpoints
- ✅ Swagger UI at `/docs`
