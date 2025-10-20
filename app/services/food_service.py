import requests
from core.config import Config

def get_food_suggestions(activity: str, city: str):
    """Get food suggestions based on activity."""
    try:
        if Config.EDAMAM_APP_ID and Config.EDAMAM_APP_KEY:
            # Simple food mapping based on activity
            food_map = {
                "office work": "coffee",
                "workout": "protein smoothie", 
                "studying": "green tea",
                "relaxing": "herbal tea",
                "traveling": "energy bar",
                "meeting friends": "sandwich"
            }
            food = food_map.get(activity, "healthy snack")
            
            url = f"https://api.edamam.com/api/food-database/v2/parser"
            params = {
                "app_id": Config.EDAMAM_APP_ID,
                "app_key": Config.EDAMAM_APP_KEY,
                "ingr": food
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("parsed"):
                calories = data["parsed"][0]["food"]["nutrients"]["ENERC_KCAL"]
                return {"food": food, "calories": f"{calories:.0f} kcal"}
    except:
        pass
    
    # Fallback
    return {"food": "healthy snack", "calories": "150 kcal"}