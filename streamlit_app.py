import streamlit as st
import requests
import json
import threading
import time
import socket
from streamlit_js_eval import get_user_agent, streamlit_js_eval

# Backend startup code
def is_port_open(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_backend():
    """Start Flask backend in background thread"""
    if not is_port_open(8000):
        print("🚀 Starting Flask backend on port 8000...")
        from agent.ritual_agent import app
        app.run(host='0.0.0.0', port=8000)
    else:
        print("✅ Backend already running on port 8000")

# Start backend automatically when Streamlit loads
if 'backend_started' not in st.session_state:
    st.session_state.backend_started = True
    if not is_port_open(8000):
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        time.sleep(3)  # Wait for backend to start

# Configure page
st.set_page_config(
    page_title="Daily Ritual AI",
    page_icon="🌟",
    layout="wide"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

def get_location_and_weather(ip=None):
    """Get user's location and weather info"""
    try:
        url = f"{BACKEND_URL}/weather"
        if ip:
            url += f"?ip={ip}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data.get("city", "New York"),
                "country": data.get("country", "United States"),
                "temperature": data.get("temperature", 22),
                "condition": data.get("condition", "pleasant")
            }
    except:
        pass
    return {"city": "New York", "country": "United States", "temperature": 22, "condition": "pleasant"}

def get_recommendation(mood, custom_mood=None, follow_up=None, force_new=False, ip=None):
    """Call backend recommendation endpoint"""
    try:
        user_mood = custom_mood if custom_mood else mood
        payload = {"activity": "general", "mood": user_mood, "force_new": force_new}
        
        if follow_up:
            payload["follow_up"] = follow_up
        if ip:
            payload["ip"] = ip
        
        response = requests.post(f"{BACKEND_URL}/api/recommend", json=payload)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def ask_question(question, ip=None):
    """Call backend ask endpoint for direct questions"""
    try:
        payload = {"question": question}
        if ip:
            payload["ip"] = ip
        response = requests.post(f"{BACKEND_URL}/api/ask", json=payload)
        return response.json() if response.status_code == 200 else None
    except:
        return None


# Get user IP using streamlit-js-eval
ip = streamlit_js_eval(
    js_expressions="fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip)",
    key="get_ip"
)

# Initialize session state
if 'location_data' not in st.session_state:
    st.session_state.location_data = get_location_and_weather(ip)

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_mood' not in st.session_state:
    st.session_state.current_mood = None

if 'show_initial_form' not in st.session_state:
    st.session_state.show_initial_form = True

if 'processing_request' not in st.session_state:
    st.session_state.processing_request = False

if 'last_action' not in st.session_state:
    st.session_state.last_action = None

if 'question_submitted' not in st.session_state:
    st.session_state.question_submitted = False



# Main UI
st.title("🌟 Daily Ritual AI")

# Get location data (only detect once per session)
if 'location_detected' not in st.session_state:
    st.session_state.location_detected = False

if not st.session_state.location_detected:
    if ip:
        with st.spinner("Detecting your location..."):
            try:
                # Set location in backend with user's IP
                requests.post(f"{BACKEND_URL}/set_location", json={"method": "ip", "ip": ip})
                # Get fresh weather data
                location_data = get_location_and_weather(ip)
                st.session_state.location_data = location_data
                st.session_state.location_detected = True
            except Exception as e:
                st.error(f"Location error: {e}")
                location_data = {"city": "New York", "country": "United States", "temperature": 22, "condition": "pleasant"}
                st.session_state.location_data = location_data
    else:
        st.info("Detecting your IP address...")
        st.stop()  # Stop execution until IP is available
else:
    # Use cached location data
    location_data = st.session_state.location_data
    
# Personalized greeting with real-time data
temp = location_data['temperature']
temp_desc = "hot" if temp > 25 else "cold" if temp < 15 else "pleasant"
city = location_data['city']

st.markdown(f"### Hi there! It's {temp_desc} ({temp}°C) in {city}. How are you feeling today?")

# Initial mood selection (only show if not set or user wants to reset)
if st.session_state.show_initial_form:
        mood_options = [
            "😊 Happy", "😴 Tired", "😰 Stressed", "💪 Energetic", 
            "😔 Sad", "🤔 Thoughtful", "😌 Calm", "🔥 Motivated"
        ]

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_mood = st.selectbox("Choose your mood:", ["Select a mood..."] + mood_options)

        with col2:
            custom_mood = st.text_input("Or describe your feeling:", placeholder="e.g., anxious, excited...")

        # Get initial recommendation
        if st.button("Get My Personalized Ritual", type="primary"):
            if selected_mood != "Select a mood..." or custom_mood:
                st.session_state.current_mood = custom_mood if custom_mood else selected_mood
                st.session_state.show_initial_form = False
                
                with st.spinner("Creating your personalized ritual..."):
                    result = get_recommendation(selected_mood, custom_mood, ip=ip)
                    
                    if result:
                        st.session_state.conversation_history.append({
                            "type": "recommendation",
                            "content": result,
                            "mood": st.session_state.current_mood
                        })
                        st.rerun()
            else:
                st.warning("Please select a mood or describe how you're feeling!")

# Show conversation history and continue interaction
if not st.session_state.show_initial_form and st.session_state.conversation_history:
        st.markdown("---")
        
        # Display conversation history first
        st.markdown("### 💬 Your Conversation")
        for i, entry in enumerate(st.session_state.conversation_history):
            if entry["type"] == "recommendation":
                st.success("✨ Your Personalized Ritual")
                st.markdown(f"**Based on feeling: {entry['mood']}**")
                st.markdown(entry["content"].get("ai_suggestion", "No suggestion available"))
                st.markdown("")
            
            elif entry["type"] == "follow_up":
                st.info(f"**You asked:** {entry['question']}")
                st.markdown(entry["response"])
                st.markdown("")

        # Add some space before action panel
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action panel at the bottom
        with st.container():
            st.markdown("### 🚀 What would you like to do next?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                change_mood = st.button("🔄 Change My Mood", use_container_width=True, key="change_mood_btn")
            
            with col2:
                new_suggestion = st.button("🔄 Get New Suggestion", use_container_width=True, key="new_suggestion_btn")
            
            with col3:
                satisfied = st.button("✅ I'm Satisfied", use_container_width=True, key="satisfied_btn")
            
            st.markdown("---")
            
            # Ask follow-up questions
            st.markdown("### ❓ Ask a Question")
            
            with st.form("question_form", clear_on_submit=True):
                follow_up_question = st.text_input("Ask anything about your ritual or request modifications:", 
                                                 placeholder="e.g., Can you suggest something healthier? What if it rains?")
                
                submitted = st.form_submit_button("💬 Ask Question", use_container_width=True)
        
        # Handle actions outside the UI rendering
        if change_mood:
            st.session_state.show_initial_form = True
            st.session_state.current_mood = None
            st.rerun()
        
        if new_suggestion:
            if st.session_state.last_action != 'new_suggestion':
                st.session_state.last_action = 'new_suggestion'
                with st.spinner("Getting a fresh suggestion..."):
                    result = get_recommendation(st.session_state.current_mood, st.session_state.current_mood, force_new=True, ip=ip)
                    if result:
                        st.session_state.conversation_history.append({
                            "type": "recommendation",
                            "content": result,
                            "mood": st.session_state.current_mood
                        })
                st.rerun()
        else:
            st.session_state.last_action = None
        
        if satisfied:
            st.balloons()
            st.success("Great! Have a wonderful day! 🌟")
        
        if submitted and follow_up_question:
            # Show immediate feedback
            st.info(f"**You asked:** {follow_up_question}")
            
            # Show loading spinner
            with st.spinner("🤔 Thinking about your question..."):
                result = ask_question(follow_up_question)
            
            if result:
                response_text = result.get("answer", "I'd be happy to help with that!")
                st.session_state.conversation_history.append({
                    "type": "follow_up",
                    "question": follow_up_question,
                    "response": response_text
                })
                # Show the response immediately
                st.success("💡 Here's my answer:")
                st.markdown(response_text)
            else:
                st.error("Sorry, I couldn't process your question. Please try again.")

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.write("Daily Ritual AI provides personalized recommendations based on:")
    st.write("• Your location & weather")
    st.write("• Your current mood")
    st.write("• AI-powered insights")
    
    if st.session_state.conversation_history:
        st.markdown("### 📝 Session Summary")
        st.write(f"Current mood: {st.session_state.current_mood}")
        st.write(f"Interactions: {len(st.session_state.conversation_history)}")
    
    st.markdown("### 🔧 Backend Status")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
        st.write("Backend will start automatically...")