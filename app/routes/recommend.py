from fastapi import APIRouter, Request
from services.weather_service import get_weather
from services.food_service import get_food_suggestions
from services.maps_service import find_nearby_places
from services.ai_service import generate_recommendation
from services.location_service import get_location_from_ip

router = APIRouter()

@router.post("/recommend")
async def recommend(request: Request):
    payload = await request.json()
    activity = payload.get("activity", "office work")

    # 1️⃣ Detect location from request IP or frontend
    ip_address = request.client.host
    location_data = get_location_from_ip(ip_address)
    city = payload.get("city", location_data["city"])
    country = location_data["country"]

    # 2️⃣ Fetch weather data
    weather = get_weather(city)

    # 3️⃣ Get food suggestion from Edamam
    food_info = get_food_suggestions(activity, city)

    # 4️⃣ AI reasoning with Bedrock
    ai_suggestion = generate_recommendation(
        city,
        country,
        weather["temperature"],
        weather["condition"],
        activity
    )

    # 5️⃣ Find nearby places (mocked)
    nearby = find_nearby_places(city, food_info["food"])

    # 6️⃣ Return response including detected location
    return {
        "detected_location": {
            "city": city,
            "country": country,
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"]
        },
        "ai_suggestion": ai_suggestion,
        "food": food_info["food"],
        "calories": food_info["calories"],
        "nearby_places": nearby
    }

@router.get("/test-location")
async def test_location(request: Request):
    """Test endpoint to check location detection from IP."""
    ip_address = request.client.host
    location_data = get_location_from_ip(ip_address)
    return {
        "client_ip": ip_address,
        "detected_location": location_data
    }
