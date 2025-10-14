def get_food_recommendation(location: dict, weather: dict, activity: str):
    """Generate food recommendation based on location, weather, and activity."""
    return f"Based on {weather.get('condition', 'current weather')} in {location.get('city', 'your area')}, try a healthy {activity}-friendly meal."