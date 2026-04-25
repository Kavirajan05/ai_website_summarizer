from fastapi import APIRouter
from app.api.routes import resume, health

api_router = APIRouter()
api_router.include_router(resume.router, tags=["resume"])
api_router.include_router(health.router, tags=["health"])
