from core.config import Config
from core.logger import setup_logger
import boto3

logger = setup_logger(__name__)

# Setup AWS session with profile
aws_session = Config.setup_aws_session()

def generate_recommendation(city: str, country: str, temperature: float, weather: str, activity: str) -> str:
    """Generate AI recommendation with fallback logic."""
    logger.info(f"Generating recommendation for {city}, {country}")
    
    # Simple recommendation logic based on context
    if temperature > 25:
        suggestion = f"It's warm in {city}! Try a refreshing iced drink or cold smoothie for your {activity}."
    elif temperature < 10:
        suggestion = f"It's chilly in {city}. A warm beverage like tea or hot chocolate would be perfect for {activity}."
    else:
        suggestion = f"Nice weather in {city}! A balanced meal or energizing snack would complement your {activity}."
    
    return suggestion
