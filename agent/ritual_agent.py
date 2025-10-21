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
    """Set user location via IP"""
    global current_location
    data = request.get_json() or {}
    ip = data.get('ip')
    location_data = get_location(ip)
    current_location = {"method": "ip", "data": location_data}
    print(f"[IP] Location set: {location_data['city']}, {location_data['country']}")
    return jsonify({"status": "success", "method": "ip", "location": location_data})

@app.route('/location')
def location():
    """Get current location"""
    ip = request.args.get('ip')
    if current_location["data"]:
        return jsonify(current_location["data"])
    return jsonify(get_location(ip))

@app.route('/weather')
def weather():
    """Get weather for current location"""
    ip = request.args.get('ip')
    return jsonify(get_weather(ip))

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    mood = data.get("mood", "neutral")
    force_new = data.get("force_new", False)
    ip = data.get("ip")
    
    location_data = get_location(ip)
    weather_data = get_weather(ip)
    
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
    ip = data.get("ip")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    if ip:
        get_location(ip)
    
    answer = ritual_agent.ask_direct_question(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)