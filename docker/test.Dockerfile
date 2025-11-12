# Test Runner Dockerfile - Pytest Execution
# Phase 6: Docker Deployment & Verification
# Author: Ram

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including Playwright dependencies)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY core/ ./core/
COPY services/ ./services/
COPY tests/ ./tests/
COPY ui/ ./ui/
COPY pytest.ini .
COPY .env.example .

# Create directories for logs and reports
RUN mkdir -p logs reports

# Set environment for pytest
ENV PYTHONUNBUFFERED=1 \
    PYTEST_ADDOPTS="--color=yes -v"

# Run pytest by default
CMD ["pytest", "-v", "--tb=short"]
