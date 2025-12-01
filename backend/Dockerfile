FROM python:3.11-slim

WORKDIR /app

# Install curl for health check (do this early for caching)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port (Azure Container Apps will route to this)
EXPOSE 8000

# Health check - Azure Container Apps uses this to verify the app is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn for production (2 workers, uvicorn worker class)
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000"]
