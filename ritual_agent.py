"""
Flask backend for Streamlit integration with Agentic AI
"""
from flask import Flask, jsonify, request
import requests
import os
from config import Config
from strands.models.bedrock import BedrockModel

# Strands agent setup
try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

class RitualAgent:
    def __init__(self):
        self.cache = {}  # Simple cache to prevent duplicate calls
        if STRANDS_AVAILABLE:
            aws_session = Config.setup_aws_session()
            if aws_session:
                Config.setup_environment()
                try:
                    model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", session=aws_session)

                    self.agent = Agent(model)
                    print(f"✅ Strands Agent initialized")
                except Exception as e:
                    print(f"Strands init error: {e}")
                    self.agent = None
            else:
                self.agent = None
        else:
            self.agent = None
    
    def generate_recommendation(self, mood, location, weather, force_new=False):
        # Create cache key
        cache_key = f"{mood}_{location}_{weather}"
        
        if self.agent:
            prompt = f"""You are Daily Ritual AI, delivering smart, context-aware food and drink suggestions to enhance daily wellness.
            
            User Context:
            - Feeling: {mood}
            - Location: {location}
            - Weather: {weather}
            
            Provide personalized recommendations focusing on:
            - Smart food suggestions tailored to mood and weather
            - Drink recommendations that complement the conditions
            - Brief wellness activities that pair with the food/drinks
            
            Use adaptive AI insights to make suggestions feel contextually perfect. Keep response warm, encouraging, under 150 words."""
            
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

    def ask_direct_question(self, question: str) -> str:
        """Direct question using fresh Strands agent to avoid caching"""
        try:            
            prompt = f"""You are Daily Ritual AI, specializing in smart, context-aware food and drink suggestions that enhance daily wellness through adaptive AI insights.
            
            Question: {question}
            
            Provide practical advice focusing on food, drinks, and wellness habits. Use your knowledge to give contextually relevant suggestions. Keep response encouraging and under 150 words."""
            
            if hasattr(self.agent, 'run'):
                result = self.agent.run(prompt)
            else:
                result = str(self.agent(prompt))
            return str(result)
            
        except Exception as e:
            print(f"Error while calling LLM: {type(e).__name__}")            
            return "Error while connecting to LLM."
        
ritual_agent = RitualAgent()
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
    
    location_data = get_location().get_json()
    weather_data = get_weather().get_json()
    
    location_str = f"{location_data['city']}, {location_data['country']}"
    weather_str = f"{weather_data['temperature']}°C, {weather_data['condition']}"
    
    # Use AI agent for recommendation
    suggestion = ritual_agent.generate_recommendation(mood, location_str, weather_str, force_new)
    
    return jsonify({
        "ai_suggestion": suggestion,
        "detected_location": {"city": location_data["city"], "country": location_data["country"]}
    })

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Direct LLM query using general knowledge within daily ritual context"""
    data = request.get_json() or {}
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    answer = ritual_agent.ask_direct_question(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)