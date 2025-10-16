# ---- Stage 1: Builder ----
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Copy only requirements first for layer caching
COPY requirements.txt ./

# Build wheelhouse (for reproducible installs)
RUN python -m pip install --upgrade pip wheel setuptools && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- Stage 2: Final runtime ----
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r app && useradd -r -g app -m -d /home/app app

WORKDIR /app

# Copy prebuilt wheels and install
COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY app /app/app

# Ensure proper permissions
RUN chown -R app:app /app
USER app

# Expose FastAPI default port
EXPOSE 8000

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Start the app using Gunicorn with Uvicorn workers
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=2 --timeout=120"

CMD ["sh", "-c", "gunicorn app.main:app -k uvicorn.workers.UvicornWorker $GUNICORN_CMD_ARGS"]
