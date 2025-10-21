"""
Location detection tool
"""
import requests
from strands.tools import tool
from flask import request, has_request_context

@tool
def get_location() -> dict:
    """Get user's current location based on their IP address"""
    
    try:
        # Fallback to public IP lookup
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        public_ip = ip_response.text.strip()
        location_response = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=5)
    
        if location_response.status_code == 200:
            data = location_response.json()
            if data["status"] == "success":
                return {
                    "city": data["city"],
                    "country": data["country"],
                    "latitude": data["lat"],
                    "longitude": data["lon"]
                }
    except:
        pass
    
    return {"city": "New York", "country": "United States", "latitude": 40.7128, "longitude": -74.0060}