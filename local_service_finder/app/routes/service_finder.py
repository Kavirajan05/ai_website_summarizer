import asyncio
from fastapi import APIRouter, BackgroundTasks
from app.models.request_model import ServiceRequest
from app.services.api_fetcher import fetch_serpapi_services
from app.services.utils import clean_business_data
from app.services.ai_analyzer import analyze_services_with_ai
from app.services.email_service import send_results_email

router = APIRouter()

async def process_service_request(request: ServiceRequest):
    # 1. Fetch data from SerpAPI (Google Local)
    print(f"Fetching {request.service} in {request.city} via SerpAPI...")
    raw_data = await fetch_serpapi_services(request.service, request.city)
    
    if not raw_data:
        print(f"No results found for {request.service} in {request.city}")
        send_results_email(
            user_email=request.email,
            ai_data={
                "service": request.service,
                "city": request.city,
                "top_recommendations": [],
                "best_choice": {},
                "summary": "We couldn't find any results for your search. Please check the service type or city name and try again.",
                "insights": []
            }
        )
        return

    # 2. Clean and Filter data (Ratings > 3.5, de-duplication)
    cleaned_data = clean_business_data(raw_data)

    if not cleaned_data:
        # Fallback if cleaning removed everything (maybe they are all low rated)
        cleaned_data = raw_data[:5]

    # 3. Analyze data using Gemini AI
    print("Performing AI Analysis...")
    ai_results = await analyze_services_with_ai(request.service, request.city, cleaned_data)

    # 4. Email the processed results
    print(f"Sending email to {request.email}...")
    await asyncio.to_thread(send_results_email, request.email, ai_results)


@router.post("/find-services")
async def find_services(request: ServiceRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_service_request, request)
    
    return {
        "status": "success",
        "message": "Results will be sent to your email shortly"
    }
