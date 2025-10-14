"""
AgentCore Gateway API Service Definitions
Deploy these services to AgentCore for external access
"""

from typing import Dict, Any
import json

class DailyRitualServices:
    """Service definitions for AgentCore Gateway"""
    
    @staticmethod
    def location_service(ip_address: str = None) -> Dict[str, Any]:
        """Location detection service for AgentCore"""
        from app.services.location_service import get_location_from_ip
        
        try:
            result = get_location_from_ip(ip_address)
            return {
                "status": "success",
                "service": "location_detection",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "location_detection",
                "error": str(e)
            }
    
    @staticmethod
    def weather_service(city: str) -> Dict[str, Any]:
        """Weather data service for AgentCore"""
        from app.services.weather_service import get_weather
        
        try:
            result = get_weather(city)
            return {
                "status": "success",
                "service": "weather_data",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "weather_data",
                "error": str(e)
            }
    
    @staticmethod
    def agent_service(context: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent service for AgentCore"""
        from app.services.agent_service import DailyRitualAgent
        
        try:
            agent = DailyRitualAgent()
            result = agent.generate_recommendation(context)
            return {
                "status": "success",
                "service": "ai_agent",
                "data": {
                    "recommendation": result,
                    "context": context
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "ai_agent",
                "error": str(e)
            }
    
    @staticmethod
    def food_service(mood: str, city: str) -> Dict[str, Any]:
        """Food recommendation service for AgentCore"""
        from app.services.food_service import get_food_suggestions
        
        try:
            result = get_food_suggestions(mood, city)
            return {
                "status": "success",
                "service": "food_recommendations",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "food_recommendations",
                "error": str(e)
            }
    
    @staticmethod
    def maps_service(city: str, food_type: str) -> Dict[str, Any]:
        """Maps/places service for AgentCore"""
        from app.services.maps_service import find_nearby_places
        
        try:
            result = find_nearby_places(city, food_type)
            return {
                "status": "success",
                "service": "nearby_places",
                "data": {
                    "places": result,
                    "city": city,
                    "search_type": food_type
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "nearby_places",
                "error": str(e)
            }

# AgentCore service registry
AGENTCORE_SERVICES = {
    "daily_ritual_location": DailyRitualServices.location_service,
    "daily_ritual_weather": DailyRitualServices.weather_service,
    "daily_ritual_agent": DailyRitualServices.agent_service,
    "daily_ritual_food": DailyRitualServices.food_service,
    "daily_ritual_maps": DailyRitualServices.maps_service,
}

# Service metadata for AgentCore registration
SERVICE_METADATA = {
    "daily_ritual_location": {
        "name": "Daily Ritual Location Service",
        "description": "Detects user location from IP address",
        "input_schema": {
            "ip_address": {"type": "string", "required": False}
        },
        "output_schema": {
            "city": "string",
            "country": "string", 
            "latitude": "number",
            "longitude": "number"
        }
    },
    "daily_ritual_weather": {
        "name": "Daily Ritual Weather Service",
        "description": "Gets weather data for a city",
        "input_schema": {
            "city": {"type": "string", "required": True}
        },
        "output_schema": {
            "temperature": "number",
            "condition": "string"
        }
    },
    "daily_ritual_agent": {
        "name": "Daily Ritual AI Agent",
        "description": "Generates personalized daily ritual recommendations",
        "input_schema": {
            "mood": {"type": "string", "required": True},
            "location": {"type": "string", "required": False},
            "weather": {"type": "string", "required": False},
            "activity": {"type": "string", "required": False}
        },
        "output_schema": {
            "recommendation": "string"
        }
    },
    "daily_ritual_food": {
        "name": "Daily Ritual Food Service", 
        "description": "Suggests food based on mood and location",
        "input_schema": {
            "mood": {"type": "string", "required": True},
            "city": {"type": "string", "required": True}
        },
        "output_schema": {
            "food": "string",
            "calories": "string"
        }
    },
    "daily_ritual_maps": {
        "name": "Daily Ritual Maps Service",
        "description": "Finds nearby places for activities",
        "input_schema": {
            "city": {"type": "string", "required": True},
            "food_type": {"type": "string", "required": True}
        },
        "output_schema": {
            "places": "array"
        }
    }
}