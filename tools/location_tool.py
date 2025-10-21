"""
Location detection tool (fixed)
"""
import requests
from strands.tools import tool
from flask import request, has_request_context

@tool
def get_location(ip: str = None) -> dict:
    """Get user's current location based on IP address (from client if available)"""
    try:
        # 1️⃣ Use passed IP if provided
        if ip:
            user_ip = ip.strip()
        elif has_request_context():
            # 2️⃣ Try headers if in Flask request context
            user_ip = (
                request.headers.get('X-Forwarded-For')
                or request.headers.get('X-Real-IP')
                or request.headers.get('CF-Connecting-IP')
                or request.environ.get('HTTP_X_FORWARDED_FOR')
                or request.remote_addr
            )
            if user_ip:
                user_ip = user_ip.split(',')[0].strip()
        else:
            user_ip = None

        # 3️⃣ Skip localhost / internal IPs
        if not user_ip or user_ip in ['127.0.0.1', '::1', 'localhost']:
            print("[get_location] Localhost or missing IP — using fallback to external IP")
            ip_response = requests.get("https://api.ipify.org", timeout=5)
            user_ip = ip_response.text.strip()

        # 4️⃣ Query ip-api with final IP
        location_response = requests.get(f"http://ip-api.com/json/{user_ip}", timeout=5)
        if location_response.status_code == 200:
            data = location_response.json()
            if data.get("status") == "success":
                print(f"[get_location] IP {user_ip} -> {data['city']}, {data['country']}")
                return {
                    "city": data["city"],
                    "country": data["country"],
                    "latitude": data["lat"],
                    "longitude": data["lon"]
                }
    except Exception as e:
        print(f"[get_location] Error: {e}")

    # 5️⃣ Fallback location (default)
    return {"city": "New York", "country": "United States", "latitude": 40.7128, "longitude": -74.0060}