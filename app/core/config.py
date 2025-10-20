import os
import boto3
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS Configuration with profile detection
    AWS_PROFILE = "Hackathon AI"
    REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Set AWS profile for boto3
    @classmethod
    def setup_aws_session(cls):
        try:
            session = boto3.Session(profile_name=cls.AWS_PROFILE)
            return session
        except Exception:
            # Fallback to default credentials
            return boto3.Session()
    
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
    EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Strands configuration
    STRANDS_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("STRANDS_API_KEY")
    STRANDS_MODEL = os.getenv("STRANDS_MODEL", "gpt-4")
    
    # Bedrock model configuration
    BEDROCK_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
