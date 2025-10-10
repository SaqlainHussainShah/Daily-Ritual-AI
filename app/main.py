from fastapi import FastAPI
from app.routes import recommend
from app.core.logger import setup_logger

logger = setup_logger("daily_ritual_ai")

app = FastAPI(title="Daily Ritual AI Backend")

app.include_router(recommend.router)

@app.get("/")
def root():
    return {"message": "Daily Ritual AI backend is live."}

# Optional: For gunicorn or uvicorn command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080)
