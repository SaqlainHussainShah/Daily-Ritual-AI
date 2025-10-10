import requests
from app.core.logger import setup_logger

logger = setup_logger(__name__)

def get_location_from_ip(ip_address: str) -> dict:
    """
    Use IP geolocation API to get user's city/country.
    """
    try:
        res = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        if res.status_code == 200:
            data = res.json()
            city = data.get("city", "Unknown")
            country = data.get("country_name", "Unknown")
            latitude = data.get("latitude", 0.0)
            longitude = data.get("longitude", 0.0)
            logger.info(f"Detected location: {city}, {country}")
            return {
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude
            }
    except Exception as e:
        logger.error(f"IP Location lookup failed: {e}")
    return {"city": "Unknown", "country": "Unknown", "latitude": 0.0, "longitude": 0.0}
