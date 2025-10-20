from core.config import Config
import os
import boto3
import json

try:
    from strands import Agent
    # Check what's available in strands
    import strands
    STRANDS_AVAILABLE = True
    print("✅ Strands Agent imported successfully")
except ImportError as e:
    STRANDS_AVAILABLE = False
    print(f"❌ Strands import failed: {e}")

class DailyRitualAgent:
    def __init__(self):
        if STRANDS_AVAILABLE:
            # Setup AWS session
            aws_session = Config.setup_aws_session()
            
            # Configure Strands to use Bedrock
            os.environ["AWS_DEFAULT_REGION"] = Config.REGION
            os.environ["AWS_PROFILE"] = Config.AWS_PROFILE
            
            # Configure Strands model via environment variable
            os.environ["STRANDS_LLM"] = f"bedrock/{Config.BEDROCK_MODEL_ID}"
            
            try:
                self.agent = Agent()
                print(f"✅ Strands Agent configured with model: {Config.BEDROCK_MODEL_ID}")
                print(f"Agent methods: {[method for method in dir(self.agent) if not method.startswith('_')]}")
            except Exception as e:
                print(f"Agent initialization error: {e}")
                self.agent = None
        else:
            self.role = "Daily Ritual Advisor"
            self.goal = "Provide personalized daily ritual recommendations"
    
    def generate_recommendation(self, context: dict) -> str:
        """Generate personalized recommendation using Strands or fallback."""
        print(f"STRANDS_AVAILABLE: {STRANDS_AVAILABLE}")
        print(f"AWS Profile: {Config.AWS_PROFILE}")
        
        if STRANDS_AVAILABLE and self.agent:
            print(f"🤖 Using Strands Agent for context: {context}")
            
            # Create prompt based on whether it's a follow-up or initial request
            if context.get('follow_up'):
                prompt = f"User is feeling {context.get('mood', 'neutral')} in {context.get('location', 'their city')}. "\
                        f"They asked: '{context.get('follow_up')}' "\
                        f"Provide a helpful, specific answer to their question about daily rituals. Keep it under 100 words."
            else:
                prompt = f"Create a personalized daily ritual recommendation for someone who is feeling {context.get('mood', 'neutral')} "\
                        f"in {context.get('location', 'their city')} where the weather is {context.get('weather', 'pleasant')}. "\
                        f"Their main activity today is {context.get('activity', 'general')}. "\
                        f"Provide specific, actionable suggestions for food/drinks, activities, and places to visit. "\
                        f"Keep the response warm, encouraging, and under 150 words."
            
            # Try different methods that might exist
            print("🚀 Starting Strands execution...")
            try:
                if hasattr(self.agent, 'run'):
                    result = self.agent.run(prompt)
                elif hasattr(self.agent, 'execute'):
                    result = self.agent.execute(prompt)
                elif hasattr(self.agent, 'generate'):
                    result = self.agent.generate(prompt)
                else:
                    result = str(self.agent(prompt))  # Try calling directly
                
                print(f"✅ Strands completed: {str(result)[:100]}...")
                return str(result)
            except Exception as e:
                print(f"Strands execution error: {e}")
                return self._fallback_recommendation(context)
        else:
            return self._fallback_recommendation(context)
    
    def _fallback_recommendation(self, context: dict) -> str:
        """Fallback recommendation logic"""
        print("⚠️ Using fallback logic - Strands not available")
        weather = context.get('weather', 'pleasant')
        location = context.get('location', 'your area')
        mood = context.get('mood', 'neutral').lower()
        
        # Mood-based recommendations
        if 'happy' in mood or 'energetic' in mood or 'motivated' in mood:
            return f"Great energy today in {location}! Try an outdoor activity, energizing smoothie, or visit a local park to maintain that positive vibe."
        elif 'tired' in mood or 'exhausted' in mood:
            return f"Time to recharge in {location}. Consider a warm herbal tea, gentle stretching, or a cozy cafe for some quiet time."
        elif 'stressed' in mood or 'anxious' in mood:
            return f"Let's find some calm in {location}. Try meditation, chamomile tea, or visit a peaceful spot like a library or garden."
        elif 'sad' in mood or 'down' in mood:
            return f"Sending comfort your way in {location}. Consider comfort food, calling a friend, or visiting an uplifting place like a bookstore."
        else:
            return f"Nice day in {location}! A balanced meal, light walk, or visiting a local cafe would be perfect for your current mood."

# Backward compatibility
def generate_ai_response(prompt: str):
    """Legacy function for backward compatibility."""
    agent = DailyRitualAgent()
    return agent.generate_recommendation({"prompt": prompt})
