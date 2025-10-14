import requests
from core.config import Config

def find_nearby_places(city: str, food_type: str):
    """Find nearby places for food/activities."""
    try:
        if Config.GOOGLE_MAPS_API_KEY:
            # Google Places API integration would go here
            pass
    except:
        pass
    
    # Mock nearby places
    return [
        f"Local Cafe - {city}",
        f"Health Food Store - {city}", 
        f"Community Center - {city}"
    ]