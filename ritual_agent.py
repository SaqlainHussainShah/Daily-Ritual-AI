"""
Flask backend for Streamlit integration with Agentic AI
"""
from flask import Flask, jsonify, request
from agent.ritual_agent import RitualAgent
from tools.location_tool import get_location
from tools.weather_tool import get_weather

ritual_agent = RitualAgent()
app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({"message": "Daily Ritual AI backend is live."})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/location')
def location():
    return jsonify(get_location())

@app.route('/weather')
def weather():
    return jsonify(get_weather())

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    mood = data.get("mood", "neutral")
    force_new = data.get("force_new", False)
    
    location_data = get_location()
    weather_data = get_weather()
    
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