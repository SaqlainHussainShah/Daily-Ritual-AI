from core.config import Config

try:
    from strands import Agent, Task
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

class DailyRitualAgent:
    def __init__(self):
        if STRANDS_AVAILABLE:
            self.agent = Agent(
                role="Daily Ritual Advisor",
                goal="Provide personalized daily ritual recommendations",
                backstory="Expert in wellness, nutrition, and lifestyle optimization"
            )
        else:
            self.role = "Daily Ritual Advisor"
            self.goal = "Provide personalized daily ritual recommendations"
    
    def generate_recommendation(self, context: dict) -> str:
        """Generate personalized recommendation using Strands or fallback."""
        if STRANDS_AVAILABLE:
            task = Task(
                description=f"Based on weather: {context.get('weather', 'unknown')}, "
                           f"location: {context.get('location', 'unknown')}, "
                           f"and user preferences, suggest a daily ritual.",
                agent=self.agent
            )
            return task.execute()
        else:
            # Fallback logic
            weather = context.get('weather', 'pleasant')
            location = context.get('location', 'your area')
            
            if 'sunny' in weather.lower():
                return f"Perfect day in {location}! Try an outdoor smoothie or iced coffee to energize your day."
            elif 'rain' in weather.lower():
                return f"Cozy weather in {location}. Consider warm tea and indoor activities for comfort."
            else:
                return f"Great day in {location}! A balanced meal and light exercise would be perfect."

# Backward compatibility
def generate_ai_response(prompt: str):
    """Legacy function for backward compatibility."""
    agent = DailyRitualAgent()
    return agent.generate_recommendation({"prompt": prompt})
