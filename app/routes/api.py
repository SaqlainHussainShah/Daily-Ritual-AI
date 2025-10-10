from fastapi import APIRouter, Request
from services.location_service import get_user_location
from services.weather_service import get_weather
from services.food_recommendation_service import get_food_recommendation

router = APIRouter()

@router.get("/recommend")
async def recommend_food(request: Request, activity: str):
    client_ip = request.client.host
    location = get_user_location(client_ip)
    weather = get_weather(location)
    recommendation = get_food_recommendation(location, weather, activity)
    
    return {
        "location": location,
        "weather": weather,
        "recommendation": recommendation
    }
