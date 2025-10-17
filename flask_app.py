from flask import Flask, jsonify, request
import requests
from config import Config
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Strands agent setup
try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

class DailyRitualAgent:
    def __init__(self):
        if STRANDS_AVAILABLE:
            # Setup AWS credentials and environment
            aws_session = Config.setup_aws_session()
            if aws_session:
                Config.setup_environment()
                
                try:
                    self.agent = Agent()
                    print(f"✅ Strands Agent with {Config.BEDROCK_MODEL_ID} initialized")
                except Exception as e:
                    print(f"Strands init error: {e}")
                    self.agent = None
            else:
                print("⚠️ AWS not available, using fallback mode")
                self.agent = None
        else:
            self.agent = None
    
    def generate_recommendation(self, context: dict) -> str:
        """Generate AI-powered recommendation"""
        if not self.agent:
            return self._fallback_recommendation(context)
        
        mood = context.get('mood', 'neutral')
        location = context.get('location', 'your area')
        weather = context.get('weather', 'pleasant weather')
        follow_up = context.get('follow_up')
        
        if follow_up:
            prompt = f"""User feeling {mood} in {location}. 
            They asked: '{follow_up}'
            Provide helpful, specific answer about daily rituals. Keep under 100 words."""
        else:
            prompt = f"""Create personalized daily ritual for someone feeling {mood} 
            in {location} with {weather}.
            
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
            return str(result)
        except Exception as e:
            print(f"AI error: {e}")
            return self._fallback_recommendation(context)
    
    def _fallback_recommendation(self, context: dict) -> str:
        """Fallback without AI"""
        mood = context.get('mood', 'neutral').lower()
        location = context.get('location', 'your area')
        
        if 'happy' in mood or 'energetic' in mood:
            return f"Great energy in {location}! Try outdoor activities, energizing smoothie, or visit a local park."
        elif 'tired' in mood:
            return f"Time to recharge in {location}. Consider herbal tea, gentle stretching, or a cozy cafe."
        elif 'stressed' in mood:
            return f"Find calm in {location}. Try meditation, chamomile tea, or visit a peaceful library."
        else:
            return f"Nice day in {location}! A balanced meal, light walk, or local cafe visit sounds perfect."
    
    def invoke(self, payload: dict, context: dict = None) -> dict:
        """AgentCore standard invoke method"""
        if context is None:
            context = {}
        
        # Extract user input
        mood = payload.get("mood", "neutral")
        follow_up = payload.get("follow_up")
        
        # Get location and weather (simplified for Flask integration)
        location = context.get('location', 'your area')
        weather = context.get('weather', 'pleasant weather')
        
        # Create AI context
        ai_context = {
            "mood": mood,
            "location": location,
            "weather": weather,
            "follow_up": follow_up
        }
        
        # Generate recommendation
        recommendation = self.generate_recommendation(ai_context)
        
        return {
            "ai_suggestion": recommendation,
            "mood": mood,
            "agent_used": self.agent is not None,
            "status": "success"
        }

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Initialize agent
    ritual_agent = DailyRitualAgent()
    
    # Store agent in app context
    app.ritual_agent = ritual_agent
    
    return app

# Initialize app with BedrockAgentCore
flask_app = create_app()
app = BedrockAgentCoreApp(flask_app)
ritual_agent = flask_app.ritual_agent

@app.route('/')
def root():
    return jsonify({"message": "Daily Ritual AI backend is live."})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "ai_enabled": STRANDS_AVAILABLE,
        "agent_ready": ritual_agent.agent is not None if STRANDS_AVAILABLE else False
    })

@app.route('/location')
def get_location():
    """Get user's location from IP"""
    try:
        # Get user's public IP
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        ip_address = ip_response.text.strip()
        
        # Get location from IP
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
    
    # Get user's location first
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
    follow_up = data.get("follow_up")
    
    # Get user's actual location and weather
    location_data = get_location().get_json()
    weather_data = get_weather().get_json()
    
    # Create context for AI agent
    context = {
        "mood": mood,
        "location": f"{location_data['city']}, {location_data['country']}",
        "weather": f"{weather_data['temperature']}°C, {weather_data['condition']}",
        "follow_up": follow_up
    }
    
    # Generate AI recommendation
    ai_suggestion = ritual_agent.generate_recommendation(context)
    
    return jsonify({
        "ai_suggestion": ai_suggestion,
        "detected_location": {"city": location_data["city"], "country": location_data["country"]}
    })

@app.route('/invoke', methods=['POST'])
def invoke_endpoint():
    """AgentCore invoke endpoint"""
    data = request.get_json() or {}
    payload = data.get("payload", {})
    context = data.get("context", {})
    
    # Get location and weather for context if not provided
    if not context.get('location') or not context.get('weather'):
        location_data = get_location().get_json()
        weather_data = get_weather().get_json()
        
        if not context.get('location'):
            context['location'] = f"{location_data['city']}, {location_data['country']}"
        if not context.get('weather'):
            context['weather'] = f"{weather_data['temperature']}°C, {weather_data['condition']}"
    
    # Call agent invoke method
    result = ritual_agent.invoke(payload, context)
    
    return jsonify(result)

# AgentCore invoke function (for direct import)
@app.entrypoint
def invoke(payload: dict, context: dict = None) -> dict:
    """BedrockAgentCore standard invoke function"""
    return ritual_agent.invoke(payload, context)

# WSGI entry point for production
def application():
    return create_app()

if __name__ == '__main__':
    # Development server
    flask_app.run(host='0.0.0.0', port=8000)