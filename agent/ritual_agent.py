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
        """
        Generate a personalized wellness recommendation based on mood, location, and weather.
        Uses cached results if available unless force_new=True.
        """
        cache_key = f"{mood}_{location}_{weather}"

        # Use cache if available
        if not force_new and cache_key in self.cache:
            return self.cache[cache_key]

        # Prepare the prompt with explicit context
        prompt = f"""
        You are Daily Ritual AI — an empathetic wellness assistant that provides 
        personalized food, drink, and activity recommendations based on the user's mood,
        location, and weather.

        User mood: {mood}
        User location: {location}
        Current weather: {weather}

        Now write a warm, encouraging response (under 150 words) that includes:
        - A food suggestion suited to the mood and weather
        - A drink recommendation that complements it
        - A simple wellness or relaxation activity that fits the vibe

        Keep the tone friendly, human, and context-aware.
        """

        try:
            if self.agent:
                if hasattr(self.agent, "run"):
                    result = self.agent.run(prompt)
                else:
                    result = str(self.agent(prompt))
            else:
                # fallback to non-agent mode
                result = self._fallback_recommendation(mood, location, weather)

            # Cache and return
            self.cache[cache_key] = str(result)
            return str(result)

        except Exception as e:
            print(f"[generate_recommendation] AI error: {e}")
            return self._fallback_recommendation(mood, location, weather)

    def _fallback_recommendation(self, mood, location, weather):
        """Local fallback recommendation if AI call fails."""
        mood_lower = mood.lower()
        if "happy" in mood_lower:
            return f"Great energy in {location}! With {weather}, enjoy an energizing smoothie, outdoor walk, or a visit to a local park."
        elif "tired" in mood_lower:
            return f"Time to recharge in {location}. With {weather}, consider herbal tea, gentle stretching, or relaxing in a cozy café."
        elif "stressed" in mood_lower:
            return f"Find calm in {location}. With {weather}, try chamomile tea, deep breathing, or a quiet moment in a peaceful space."
        else:
            return f"Enjoy your day in {location}! With {weather}, a balanced meal, light walk, or mindful break would be perfect."

    def ask_direct_question(self, question: str, location: str = None, weather: str = None) -> str:
        """
        Handle user follow-up questions about their ritual, considering location and weather.
        Uses LLM if available; falls back to a simple rule-based reply otherwise.
        """
        prompt = f"""
        You are Daily Ritual AI — an empathetic, wellness-focused assistant
        that provides adaptive food, drink, and self-care guidance.

        The user has a question about their daily ritual.

        Question: {question}
        Location: {location or 'Unknown'}
        Weather: {weather or 'Unknown'}

        Give a short, practical, and encouraging response (under 120 words)
        that directly addresses the question — ideally including:
        - A relevant food or drink idea
        - A simple wellness or mindfulness tip
        Keep the tone warm and human-like.
        """

        try:
            if self.agent:
                if hasattr(self.agent, "run"):
                    result = self.agent.run(prompt)
                else:
                    result = str(self.agent(prompt))
                return str(result)
            else:
                return self._fallback_question_response(question, location, weather)
        except Exception as e:
            print(f"[ask_direct_question] Error: {e}")
            return self._fallback_question_response(question, location, weather)


    def _fallback_question_response(self, question, location, weather):
        """Fallback reply if LLM is unavailable."""
        base = f"In {location or 'your area'}, with {weather or 'the current weather'}, "
        if "rain" in question.lower():
            return base + "you might enjoy a warm herbal tea and a cozy book indoors."
        elif "energy" in question.lower():
            return base + "try a smoothie with banana and oats to boost your energy naturally."
        elif "stress" in question.lower() or "anxious" in question.lower():
            return base + "deep breathing and a calming tea like chamomile could help."
        else:
            return base + "a balanced meal, hydration, and a short walk are always good choices."

# Location and weather storage
current_location = {"method": "ip", "data": None}
cached_weather = {"data": None, "timestamp": 0}



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
    ip = data.get('ip') or data.get('ip_address')
    location_data = get_location(ip)
    current_location = {"method": "ip", "data": location_data, "user_ip": ip}
    print(f"[IP] Location set: {location_data['city']}, {location_data['country']} (IP: {ip})")
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
    global current_location
    try:
        data = request.get_json() or {}
        mood = data.get("mood", "neutral")
        force_new = data.get("force_new", False)
        ip = data.get("ip")
        
        print(f"[RECOMMEND] Request data: {data}")
        
        # Use stored location if available, otherwise get fresh location
        if current_location["data"] and current_location.get("user_ip") == ip:
            location_data = current_location["data"]
        else:
            location_data = get_location(ip)
            current_location = {"method": "ip", "data": location_data, "user_ip": ip}
        
        weather_data = get_weather(ip)
        
        location_str = f"{location_data['city']}, {location_data['country']}"
        weather_str = f"{weather_data['temperature']}°C, {weather_data['condition']}"
        
        print(f"[RECOMMEND] Using location: {location_str} for mood: {mood}")
        
        suggestion = ritual_agent.generate_recommendation(mood, location_str, weather_str, force_new)
        
        result = {
            "ai_suggestion": suggestion,
            "detected_location": {"city": location_data["city"], "country": location_data["country"]}
        }
        
        print(f"[RECOMMEND] Result: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"[RECOMMEND] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    global current_location
    data = request.get_json() or {}
    question = data.get("question", "")
    ip = data.get("ip")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Use stored location data to maintain consistency
    if current_location["data"] and current_location.get("user_ip") == ip:
        location_data = current_location["data"]
        
        # Use cached weather if available (cache for 10 minutes)
        import time
        current_time = time.time()
        if cached_weather["data"] and (current_time - cached_weather["timestamp"]) < 600:
            weather_data = cached_weather["data"]
            print(f"[ASK] Using cached weather data")
        else:
            # Get fresh weather data
            try:
                api_key = Config.OPENWEATHER_API_KEY
                if location_data.get("latitude") and location_data.get("longitude"):
                    url = f"http://api.openweathermap.org/data/2.5/weather?lat={location_data['latitude']}&lon={location_data['longitude']}&appid={api_key}&units=metric"
                else:
                    url = f"http://api.openweathermap.org/data/2.5/weather?q={location_data['city']}&appid={api_key}&units=metric"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    weather_json = response.json()
                    weather_data = {
                        "temperature": round(weather_json["main"]["temp"], 1),
                        "condition": weather_json["weather"][0]["description"]
                    }
                    # Cache the weather data
                    cached_weather = {"data": weather_data, "timestamp": current_time}
                    print(f"[ASK] Fetched fresh weather data")
                else:
                    weather_data = {"temperature": 22, "condition": "clear sky"}
            except:
                weather_data = {"temperature": 22, "condition": "clear sky"}
    else:
        location_data = get_location(ip)
        weather_data = get_weather(ip)
        current_location = {"method": "ip", "data": location_data, "user_ip": ip}

    location_str = f"{location_data['city']}, {location_data['country']}"
    weather_str = f"{weather_data['temperature']}°C, {weather_data['condition']}"

    print(f"[ASK] Using location: {location_str} for question: {question}")
    
    answer = ritual_agent.ask_direct_question(question, location_str, weather_str)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)