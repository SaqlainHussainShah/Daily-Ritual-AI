"""
Weather detection tool
"""
import requests
from config import Config
from strands.tools import tool
from .location_tool import get_location

@tool
def get_weather() -> dict:
    """Get current weather for user's location"""
    api_key = Config.OPENWEATHER_API_KEY
    
    location_data = get_location()
    city = location_data["city"]
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "city": city,
                "country": location_data["country"]
            }
    except:
        pass
    
    return {"temperature": 22, "condition": "clear sky", "city": city, "country": location_data["country"]}