import requests
from app.core.config import Config
from app.core.logger import setup_logger

logger = setup_logger(__name__)

def get_weather(city: str) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        logger.info(f"Fetched weather for {city}")
        return {
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"]
        }
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return {"temperature": None, "condition": "Unavailable"}
