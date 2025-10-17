"""
Simple Flask backend for Streamlit integration with AI
"""
from flask import Flask, jsonify, request
import requests
import os
from config import Config

# Strands agent setup
try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

class SimpleRitualAgent:
    def __init__(self):
        self.cache = {}  # Simple cache to prevent duplicate calls
        if STRANDS_AVAILABLE:
            aws_session = Config.setup_aws_session()
            if aws_session:
                Config.setup_environment()
                try:
                    self.agent = Agent()
                    print(f"✅ Strands Agent initialized")
                except Exception as e:
                    print(f"Strands init error: {e}")
                    self.agent = None
            else:
                self.agent = None
        else:
            self.agent = None
    
    def answer_question(self, question, mood, location, weather):
        """Answer user's follow-up question"""
        if self.agent:
            prompt = f"""User is feeling {mood} in {location} with {weather} weather.
            
            They asked: "{question}"
            
            Provide a helpful, personalized answer related to daily rituals, wellness, activities, food, or lifestyle suggestions. Keep it conversational and under 100 words."""
            
            try:
                if hasattr(self.agent, 'run'):
                    result = self.agent.run(prompt)
                else:
                    result = str(self.agent(prompt))
                return str(result)
            except Exception as e:
                print(f"AI error: {e}")
        
        return "I'd be happy to help with that! Could you be more specific about what you'd like to know?"
    
    def generate_recommendation(self, mood, location, weather, force_new=False):
        # Create cache key
        cache_key = f"{mood}_{location}_{weather}"
        
        # Check cache first (unless force_new is True)
        if not force_new and cache_key in self.cache:
            print("Using cached response")
            return self.cache[cache_key]
        
        if self.agent:
            prompt = f"""Create a personalized daily ritual for someone feeling {mood} 
            in {location} with {weather} weather.
            
            Provide specific suggestions for:
            - Food/drinks
            - Activities 
            - Places to visit
            
            Keep warm, encouraging, under 150 words."""
            
            try:
                if hasattr(self.agent, 'run'):
                    result = self.agent.run(prompt)
                else:
                    result = str(self.agent(prompt))
                
                # Cache the result
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

ritual_agent = SimpleRitualAgent()
app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({"message": "Daily Ritual AI backend is live."})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/location')
def get_location():
    """Get user's location from IP"""
    try:
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        ip_address = ip_response.text.strip()
        
        location_response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        if location_response.status_code == 200:
            data = location_response.json()
            if data["status"] == "success":
                return jsonify({
                    "city": data["city"],
                    "country": data["country"],
                    "latitude": data["lat"],
                    "longitude": data["lon"]
                })
    except:
        pass
    
    return jsonify({"city": "New York", "country": "United States", "latitude": 40.7128, "longitude": -74.0060})

@app.route('/weather')
def get_weather():
    """Get weather for user's actual location"""
    api_key = Config.OPENWEATHER_API_KEY
    
    location_data = get_location().get_json()
    city = location_data["city"]
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "city": city,
                "country": location_data["country"]
            })
    except:
        pass
    
    return jsonify({"temperature": 22, "condition": "clear sky", "city": city, "country": location_data["country"]})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    mood = data.get("mood", "neutral")
    force_new = data.get("force_new", False)
    follow_up = data.get("follow_up")
    
    location_data = get_location().get_json()
    weather_data = get_weather().get_json()
    
    location_str = f"{location_data['city']}, {location_data['country']}"
    weather_str = f"{weather_data['temperature']}°C, {weather_data['condition']}"
    
    if follow_up:
        # Handle follow-up questions
        suggestion = ritual_agent.answer_question(follow_up, mood, location_str, weather_str)
        return jsonify({
            "ai_response": suggestion,
            "detected_location": {"city": location_data["city"], "country": location_data["country"]}
        })
    else:
        # Use AI agent for recommendation
        suggestion = ritual_agent.generate_recommendation(mood, location_str, weather_str, force_new)
        return jsonify({
            "ai_suggestion": suggestion,
            "detected_location": {"city": location_data["city"], "country": location_data["country"]}
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)