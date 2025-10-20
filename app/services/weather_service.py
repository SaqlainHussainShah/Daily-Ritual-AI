import requests
from core.config import Config

def get_weather(city: str):
    """Get weather data for a city."""
    try:
        if Config.OPENWEATHER_API_KEY:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"]
            }
    except:
        pass
    
    # Mock data fallback
    return {"temperature": 22, "condition": "clear sky"}