import os
import boto3

class Config:
    # AWS Configuration - Use environment variables for EB
    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    
    # Bedrock model configuration
    BEDROCK_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    # OpenWeather API
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "5de0650c2a6fd75c5f27efcba7264c54")
    
    @classmethod
    def setup_aws_session(cls):
        """Setup AWS session for Elastic Beanstalk"""
        try:
            # Use IAM role credentials (no profile needed)
            session = boto3.Session(region_name=cls.AWS_REGION)
            return session
        except Exception as e:
            print(f"AWS session failed: {e}")
            return None
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables for Strands"""
        os.environ["AWS_DEFAULT_REGION"] = cls.AWS_REGION
        # Remove AWS_PROFILE - not needed in EB
        if "AWS_PROFILE" in os.environ:
            del os.environ["AWS_PROFILE"]
        