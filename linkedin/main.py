from fastapi import FastAPI
from routes.analyze import router as analyze_router
from routes.report import router as report_router
from routes.email import router as email_router

app = FastAPI(title="LinkedIn Profile Analyzer")

app.include_router(analyze_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(email_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "LinkedIn Analyzer API Running"}