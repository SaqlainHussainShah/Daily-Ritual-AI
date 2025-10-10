import boto3
from core.config import Config

def generate_ai_response(prompt: str):
    """Use AWS Bedrock (Claude or Titan) to generate recommendation."""
    try:
        client = boto3.client("bedrock-runtime", region_name=Config.AWS_REGION)
        response = client.invoke_model(
            modelId=Config.BEDROCK_MODEL,
            body=f'{{"prompt": "{prompt}"}}'
        )
        result = response["body"].read().decode("utf-8")
        return result
    except Exception as e:
        # fallback for local development
        return f"[MOCK RESPONSE] {prompt} → Try a mango smoothie or coffee based on your weather and mood."
