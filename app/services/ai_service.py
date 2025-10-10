import boto3
from langchain.llms import Bedrock
from langchain import PromptTemplate, LLMChain
from app.core.config import Config
from app.core.logger import setup_logger

logger = setup_logger(__name__)

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=Config.REGION
)

template = """
You are Daily Ritual AI, a wellness assistant.
Context:
City: {city}, {country}
Temperature: {temperature}°C
Weather: {weather}
User Activity: {activity}

Recommend ONE suitable local food or drink with calorie info and reasoning. 
The suggestion should reflect common preferences or ingredients available in {country}.
"""
prompt = PromptTemplate(template=template, input_variables=["city", "country", "temperature", "weather", "activity"])

llm = Bedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)
chain = LLMChain(llm=llm, prompt=prompt)

def generate_recommendation(city: str, country: str, temperature: float, weather: str, activity: str) -> str:
    logger.info(f"Generating recommendation for {city}, {country}")
    try:
        response = chain.run({
            "city": city,
            "country": country,
            "temperature": temperature,
            "weather": weather,
            "activity": activity
        })
        return response.strip()
    except Exception as e:
        logger.error(f"Bedrock error: {e}")
        return "Unable to generate suggestion right now."
