# API Service Dockerfile - FastAPI Locator Repair Service
# Phase 6: Docker Deployment & Verification
# Author: Ram

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY services/ ./services/
COPY scripts/ ./scripts/
COPY pytest.ini .
COPY .env.example .

# Create directories for logs and reports
RUN mkdir -p logs reports

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API service
CMD ["uvicorn", "services.locator_repair.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
