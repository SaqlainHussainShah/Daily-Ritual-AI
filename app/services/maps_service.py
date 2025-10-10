def find_nearby_places(city: str, item: str) -> list:
    """Return mock nearby places for now."""
    return [
        {"name": f"{item} Bar - {city} Center", "price": "AED 20"},
        {"name": f"{item} Hub - Downtown {city}", "price": "AED 18"}
    ]
