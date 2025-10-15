from fastapi import FastAPI, Request
from routes import recommend
from core.logger import setup_logger

logger = setup_logger("daily_ritual_ai")

app = FastAPI(title="Daily Ritual AI Backend")

app.include_router(recommend.router, prefix="/api")

# Add direct endpoints for testing
@app.get("/test-location")
async def test_location_direct(request: Request):
    """Direct test endpoint for location detection."""
    from fastapi import Request
    from services.location_service import get_location_from_ip
    
    ip_address = request.client.host
    location_data = get_location_from_ip(ip_address)
    return {
        "client_ip": ip_address,
        "detected_location": location_data
    }

@app.get("/")
def root():
    return {"message": "Daily Ritual AI backend is live."}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Optional: For gunicorn or uvicorn command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080)
