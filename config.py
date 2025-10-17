import os
import boto3

class Config:
    # AWS Configuration
    AWS_PROFILE = "Hackathon AI"
    AWS_REGION = "us-east-1"
    
    # Bedrock model configuration
    BEDROCK_MODEL_ID = "us.anthropic.claude-3-5-sonnet-20250219-v1:0"
    
    # OpenWeather API
    OPENWEATHER_API_KEY = "5de0650c2a6fd75c5f27efcba7264c54"
    
    @classmethod
    def setup_aws_session(cls):
        """Setup AWS session with profile"""
        try:
            session = boto3.Session(profile_name=cls.AWS_PROFILE)
            print(f"✅ AWS profile '{cls.AWS_PROFILE}' loaded")
            return session
        except Exception:
            session = boto3.Session()
            print("⚠️ Using default AWS credentials")
            return session
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables for Strands"""
        os.environ["AWS_DEFAULT_REGION"] = cls.AWS_REGION
        os.environ["AWS_PROFILE"] = cls.AWS_PROFILE
        os.environ["STRANDS_LLM"] = f"bedrock/{cls.BEDROCK_MODEL_ID}"