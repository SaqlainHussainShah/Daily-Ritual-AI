"""
Daily Ritual AI Agent
"""
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from config import Config
from strands.models.bedrock import BedrockModel
from tools.location_tool import get_location
from tools.weather_tool import get_weather
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import requests

try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

class RitualAgent:
    def __init__(self):
        self.cache = {}
        if STRANDS_AVAILABLE:
            aws_session = Config.setup_aws_session()
            if aws_session:
                Config.setup_environment()
                try:
                    model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", session=aws_session)
                    self.agent = Agent(model, tools=[get_location, get_weather])
                    print(f"✅ Strands Agent initialized with tools")
                except Exception as e:
                    print(f"Strands init error: {e}")
                    self.agent = None
            else:
                self.agent = None
        else:
            self.agent = None
    
    def generate_recommendation(self, mood, location, weather, force_new=False):
        cache_key = f"{mood}_{location}_{weather}"
        
        if self.agent:
            prompt = f"""You are Daily Ritual AI, delivering smart, context-aware food and drink suggestions to enhance daily wellness.
            
            User is feeling: {mood}
            
            Use the get_location and get_weather tools to get current context, then provide personalized recommendations focusing on:
            - Smart food suggestions tailored to mood and weather
            - Drink recommendations that complement the conditions
            - Brief wellness activities that pair with the food/drinks
            
            Use adaptive AI insights to make suggestions feel contextually perfect. Keep response warm, encouraging, under 150 words."""
            
            try:
                if hasattr(self.agent, 'run'):
                    result = self.agent.run(prompt)
                else:
                    result = str(self.agent(prompt))
                
                self.cache[cache_key] = str(result)
                return str(result)
            except Exception as e:
                print(f"AI error: {e}")
        
        # Fallback
        if 'happy' in mood.lower():
            return f"Great energy in {location}! With {weather}, try outdoor activities, energizing smoothie, or visit a local park."
        elif 'tired' in mood.lower():
            return f"Time to recharge in {location}. With {weather}, consider herbal tea, gentle stretching, or a cozy cafe."
        elif 'stressed' in mood.lower():
            return f"Find calm in {location}. With {weather}, try meditation, chamomile tea, or visit a peaceful library."
        else:
            return f"Nice day in {location}! With {weather}, a balanced meal, light walk, or local cafe visit sounds perfect."

    def ask_direct_question(self, question: str) -> str:
        try:            
            prompt = f"""You are Daily Ritual AI, specializing in smart, context-aware food and drink suggestions that enhance daily wellness through adaptive AI insights.
            
            Question: {question}
            
            Use the get_location and get_weather tools if needed for context. Provide practical advice focusing on food, drinks, and wellness habits. Keep response encouraging and under 150 words."""
            
            if hasattr(self.agent, 'run'):
                result = self.agent.run(prompt)
            else:
                result = str(self.agent(prompt))
            return str(result)
            
        except Exception as e:
            print(f"Error while calling LLM: {type(e).__name__}")            
            return "Error while connecting to LLM."

# Location storage
current_location = {"method": "ip", "data": None}

def get_location_from_gps(latitude, longitude):
    """Get location from GPS coordinates"""
    try:
        geolocator = Nominatim(user_agent="daily-ritual-ai")
        location = geolocator.reverse((latitude, longitude), timeout=10)
        
        if location:
            addr = location.raw.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
            country = addr.get("country") or "Unknown"
            
            return {
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude
            }
    except Exception as e:
        print(f"GPS geocoding error: {e}")
    return None

def get_location_from_ip():
    """Get location from IP address"""
    try:
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        ip_address = ip_response.text.strip()
        
        location_response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        if location_response.status_code == 200:
            data = location_response.json()
            if data["status"] == "success":
                return {
                    "city": data["city"],
                    "country": data["country"],
                    "latitude": data["lat"],
                    "longitude": data["lon"]
                }
    except Exception as e:
        print(f"IP location error: {e}")
    
    return {"city": "New York", "country": "United States", "latitude": 40.7128, "longitude": -74.0060}

# Flask app setup
from flask import Flask, jsonify, request

app = Flask(__name__)
ritual_agent = RitualAgent()

@app.route('/')
def root():
    return jsonify({"message": "Daily Ritual AI backend is live."})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/set_location', methods=['POST'])
def set_location():
    """Set user location via GPS or IP"""
    global current_location
    data = request.get_json() or {}
    method = data.get("method", "ip")
    
    if method == "gps":
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude and longitude:
            location_data = get_location_from_gps(latitude, longitude)
            if location_data:
                current_location = {"method": "gps", "data": location_data}
                print(f"[GPS] Location set: {location_data['city']}, {location_data['country']}")
                return jsonify({"status": "success", "method": "gps", "location": location_data})
    
    # Fallback to IP
    location_data = get_location_from_ip()
    current_location = {"method": "ip", "data": location_data}
    print(f"[IP] Location set: {location_data['city']}, {location_data['country']}")
    return jsonify({"status": "success", "method": "ip", "location": location_data})

@app.route('/location')
def location():
    """Get current location"""
    if current_location["data"]:
        return jsonify(current_location["data"])
    return jsonify(get_location_from_ip())

@app.route('/weather')
def weather():
    """Get weather for current location"""
    location_data = current_location["data"] if current_location["data"] else get_location_from_ip()
    
    try:
        from config import Config
        api_key = Config.OPENWEATHER_API_KEY
        
        if location_data.get("latitude") and location_data.get("longitude"):
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={location_data['latitude']}&lon={location_data['longitude']}&appid={api_key}&units=metric"
        else:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location_data['city']}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "city": location_data["city"],
                "country": location_data["country"]
            })
    except Exception as e:
        print(f"Weather error: {e}")
    
    return jsonify({
        "temperature": 22, 
        "condition": "clear sky", 
        "city": location_data.get("city", "Unknown"), 
        "country": location_data.get("country", "Unknown")
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    mood = data.get("mood", "neutral")
    force_new = data.get("force_new", False)
    
    location_data = get_location()
    weather_data = get_weather()
    
    location_str = f"{location_data['city']}, {location_data['country']}"
    weather_str = f"{weather_data['temperature']}°C, {weather_data['condition']}"
    
    suggestion = ritual_agent.generate_recommendation(mood, location_str, weather_str, force_new)
    
    return jsonify({
        "ai_suggestion": suggestion,
        "detected_location": {"city": location_data["city"], "country": location_data["country"]}
    })

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.get_json() or {}
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    answer = ritual_agent.ask_direct_question(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)