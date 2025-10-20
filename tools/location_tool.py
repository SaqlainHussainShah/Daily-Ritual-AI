"""
Location detection tool
"""
import requests
from strands.tools import tool
from flask import request, has_request_context

@tool
def get_location() -> dict:
    """Get user's current location based on their IP address"""
    user_ip = None
    
    # Get user's IP from Flask request if available
    if has_request_context():
        user_ip = request.headers.get('X-Forwarded-For', 
                                     request.headers.get('X-Real-IP', 
                                                        request.remote_addr))
        if user_ip:
            user_ip = user_ip.split(',')[0].strip()
    
    try:
        # Use user's actual IP if available and not local
        if user_ip and user_ip != '127.0.0.1' and not user_ip.startswith('192.168.'):
            location_response = requests.get(f"http://ip-api.com/json/{user_ip}", timeout=5)
        else:
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