import streamlit as st
import requests
import json

# Configure page
st.set_page_config(
    page_title="Daily Ritual AI",
    page_icon="🌟",
    layout="wide"
)

# Backend URL
BACKEND_URL = "http://localhost:8080"

def get_recommendation(activity, city=None):
    """Call backend recommendation endpoint"""
    try:
        payload = {"activity": activity}
        if city:
            payload["city"] = city
        
        response = requests.post(f"{BACKEND_URL}/api/recommend", json=payload)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Main UI
st.title("🌟 Daily Ritual AI")
st.subheader("Get personalized recommendations for your day")

# Input section
col1, col2 = st.columns(2)

with col1:
    activity = st.selectbox(
        "What's your main activity today?",
        ["office work", "workout", "studying", "relaxing", "traveling", "meeting friends"]
    )

with col2:
    city = st.text_input("City (optional)", placeholder="Auto-detect from IP")

# Get recommendation button
if st.button("Get My Daily Ritual", type="primary"):
    with st.spinner("Generating your personalized recommendation..."):
        result = get_recommendation(activity, city)
        
        if result:
            # Display results
            st.success("✨ Your Daily Ritual is Ready!")
            
            # Location info
            location = result.get("detected_location", {})
            st.info(f"📍 **Location:** {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}")
            
            # AI Suggestion
            st.markdown("### 🤖 AI Recommendation")
            st.markdown(result.get("ai_suggestion", "No suggestion available"))
            
            # Food recommendation
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🍽️ Food Suggestion")
                st.write(f"**Food:** {result.get('food', 'N/A')}")
                st.write(f"**Calories:** {result.get('calories', 'N/A')}")
            
            with col2:
                st.markdown("### 📍 Nearby Places")
                places = result.get("nearby_places", [])
                if places:
                    for place in places[:3]:  # Show top 3
                        st.write(f"• {place}")
                else:
                    st.write("No nearby places found")
        else:
            st.error("❌ Unable to get recommendation. Make sure the backend is running.")

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.write("Daily Ritual AI provides personalized recommendations based on:")
    st.write("• Your location & weather")
    st.write("• Current activity")
    st.write("• AI-powered insights")
    
    st.markdown("### 🔧 Backend Status")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
        st.write("Start backend with: `uvicorn app.main:app --reload`")