from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import service_finder

app = FastAPI(
    title="Local Service Finder API",
    description="An AI-powered system to find, analyze, and rank local service providers and dispatch summaries via email.",
    version="1.0.0"
)

# Optional: Add CORS middleware if needed later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(service_finder.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Local Service Finder API",
        "docs": "Visit /docs for the API documentation"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
