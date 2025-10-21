"""
Location detection tool
"""
import requests
from strands.tools import tool
from flask import request, has_request_context

@tool
def get_location(ip: str = None) -> dict:
    """Get user's current location based on their IP address"""
    
    try:
        user_ip = ip
        if not user_ip and has_request_context():
            if request.headers.get("X-Forwarded-For"):
                user_ip = request.headers.get("X-Forwarded-For").split(",")[0]
            else:
                user_ip = request.remote_addr
        
        if user_ip:
            location_response = requests.get(f"http://ip-api.com/json/{user_ip}", timeout=5)
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