# Base: slim + no cache to keep small
FROM python:3.11-slim

# (Optional) set a non-root user
RUN useradd -m appuser

# Install system deps (if you need build tools, add: gcc build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pre-copy requirements for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Cloud Run provides PORT env var; default to 8080 locally
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Switch to non-root
USER appuser

# Start Uvicorn; bind to 0.0.0.0 and $PORT for Cloud Run
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
