import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REGION = os.getenv("AWS_REGION", "us-east-1")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
    EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
