from fastapi import FastAPI
from routes import summarize
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Summarizer API",
    description="A production-ready API to summarize YouTube videos and email the results.",
    version="1.0.0"
)

# Include the summarize router
app.include_router(summarize.router, prefix="/api", tags=["summarization"])

@app.get("/")
async def root():
    """
    Root endpoint for a simple health check.
    """
    return {"status": "YouTube Summarizer API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
