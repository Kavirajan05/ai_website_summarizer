from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes.summarize import router as summarize_router

app = FastAPI(
    title="AI Website Summarizer API",
    description="API to scrape websites, analyze with LLM, and send email reports.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the summarize router
app.include_router(summarize_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Website Summarizer API."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
