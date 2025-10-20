import requests

def get_location_from_ip(ip_address: str):
    """Get location data from IP address."""
    try:
        # For localhost, get real public IP
        if not ip_address or ip_address == "127.0.0.1":
            # Get public IP first
            public_ip_response = requests.get("https://api.ipify.org")
            ip_address = public_ip_response.text.strip()
            print(f"Detected public IP: {ip_address}")  # Debug
        
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        print(f"API Response: {data}")  # Debug
        
        if data["status"] == "success":
            return {
                "city": data["city"],
                "country": data["country"],
                "latitude": data["lat"],
                "longitude": data["lon"]
            }
    except Exception as e:
        print(f"Location error: {e}")  # Debug
    
    # Fallback for localhost/development
    return {
        "city": "New York",
        "country": "United States", 
        "latitude": 40.7128,
        "longitude": -74.0060
    }