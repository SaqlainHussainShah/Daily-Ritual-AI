import requests
from app.core.config import Config
from app.core.logger import setup_logger

logger = setup_logger(__name__)

def get_food_suggestions(activity: str, city: str) -> dict:
    """Get food or drink suggestion from Edamam API."""
    query = f"{activity} drink" if "gym" in activity.lower() else "healthy food"
    url = f"https://api.edamam.com/api/food-database/v2/parser?app_id={Config.EDAMAM_APP_ID}&app_key={Config.EDAMAM_APP_KEY}&ingr={query}"

    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        hints = data.get("hints", [])
        if hints:
            food_label = hints[0]["food"]["label"]
            calories = hints[0]["food"]["nutrients"].get("ENERC_KCAL", "N/A")
            logger.info(f"Food suggestion for {activity}: {food_label}")
            return {"food": food_label, "calories": calories}
    except Exception as e:
        logger.error(f"Food API error: {e}")

    return {"food": "Protein Shake", "calories": 200}
