# Dashboard Service Dockerfile - Streamlit Vision Dashboard
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
COPY ui/ ./ui/
COPY docs/ ./docs/
COPY .env.example .

# Create directories for logs and reports
RUN mkdir -p logs reports

# Expose Streamlit port
EXPOSE 8501

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit dashboard
CMD ["streamlit", "run", "ui/vision_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
