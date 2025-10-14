"""
services package
----------------
Implements service-layer logic for Daily Ritual AI.

Includes:
- Location detection (via IP)
- Weather data retrieval
- AI agent orchestration (LangChain/Bedrock)
- Food recommendation generation

Each module is stateless and reusable.

Example:
    from services import get_user_location, get_weather, get_food_recommendation
"""

from .location_service import get_location_from_ip
from .weather_service import get_weather
from .food_recommendation_service import get_food_recommendation
from .agent_service import generate_ai_response
from .ai_service import generate_recommendation
from .maps_service import find_nearby_places

__all__ = [
    "get_user_location",
    "get_weather",
    "get_food_recommendation",
    "generate_ai_response",
    "generate_recommendation",
    "find_nearby_places"
]
