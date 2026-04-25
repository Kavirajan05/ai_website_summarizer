from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes.summarize import router as summarize_router
from app.routes.service_finder import router as service_finder_router

app = FastAPI(
    title="AI Automation Hub",
    description="Multi-service AI automation backend (Website/YouTube Summarizer & Local Service Finder).",
    version="1.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarize_router)
app.include_router(service_finder_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Website Summarizer API."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
