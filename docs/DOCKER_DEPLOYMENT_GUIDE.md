# Docker Deployment Guide

**Dockerized AI TestOps Environment**

Phase 6: Docker Deployment & Verification  
Author: Ram  
Repository: SDET-AI-Labs/ai-powered-test-automation

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Services](#services)
6. [Build & Run](#build--run)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)
9. [Performance](#performance)
10. [Production Deployment](#production-deployment)

---

## 🎯 Overview

This guide covers deploying the entire **AI Test Automation Framework** using Docker and Docker Compose. The stack includes:

- **API Service** (FastAPI) - Locator repair REST API on port 8000
- **Dashboard Service** (Streamlit) - Vision Dashboard UI on port 8501
- **Test Runner** (Pytest) - Automated test execution

### Key Benefits

✅ **Reproducible** - Same environment everywhere  
✅ **Isolated** - No dependency conflicts  
✅ **Portable** - Works on Windows, Mac, Linux  
✅ **Scalable** - Easy to orchestrate multiple instances  
✅ **Fast** - Containerized startup in seconds

---

## 🏗️ Architecture

### Container Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host                               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API        │  │  Dashboard   │  │  Test Runner │     │
│  │  Container   │  │  Container   │  │  Container   │     │
│  │              │  │              │  │              │     │
│  │  FastAPI     │  │  Streamlit   │  │  Pytest      │     │
│  │  Port: 8000  │  │  Port: 8501  │  │  (on-demand) │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────┬───────┴──────────────────┘              │
│                    │                                         │
│            ┌───────▼────────┐                                │
│            │  ai_testops    │                                │
│            │  Network       │                                │
│            └────────────────┘                                │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Shared Volumes                             │   │
│  │  ./logs  ───→  /app/logs  (all containers)         │   │
│  │  ./reports ──→  /app/reports (all containers)      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Test Runner executes tests
   ↓
2. Tests call API Service (locator repair)
   ↓
3. API generates healing logs → ./logs/
   ↓
4. Dashboard reads logs from shared volume
   ↓
5. Dashboard displays metrics & reports
```

---

## 📦 Prerequisites

### Required Software

1. **Docker Desktop** (v20.10+)
   - Windows: https://www.docker.com/products/docker-desktop
   - Mac: https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt-get install docker-ce docker-compose-plugin`

2. **Docker Compose** (v2.0+)
   - Usually included with Docker Desktop
   - Verify: `docker-compose --version`

3. **Git** (for cloning repository)

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| Disk Space | 5 GB | 10 GB |
| CPU Cores | 2 | 4 |

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/SDET-AI-Labs/ai-powered-test-automation.git
cd ai-powered-test-automation
```

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
VISION_PROVIDER=gemini
```

### 3. Build All Services

```bash
docker-compose build
```

Expected output:
```
[+] Building 120.3s (45/45) FINISHED
 => [api] ...
 => [dashboard] ...
 => [tests] ...
Successfully built ai_test_foundation
```

### 4. Start Services

```bash
# Start API and Dashboard
docker-compose up -d api dashboard

# Verify services are running
docker-compose ps
```

### 5. Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Open Dashboard in browser
# Navigate to: http://localhost:8501
```

---

## 🔧 Services

### API Service

**Container:** `ai_locator_api`  
**Port:** 8000  
**Purpose:** FastAPI-based locator repair service

#### Endpoints

- **GET `/health`** - Health check
  ```json
  {
    "status": "healthy",
    "service": "locator-repair-service",
    "version": "1.0.0"
  }
  ```

- **GET `/docs`** - Swagger UI
  - URL: http://localhost:8000/docs

- **POST `/repair`** - Repair locator
  ```json
  {
    "framework": "playwright",
    "failed_locator": "button#old",
    "context_hint": "Submit button",
    "html_snapshot": "<html>...</html>"
  }
  ```

#### Configuration

- **Dockerfile:** `docker/api.Dockerfile`
- **Base Image:** `python:3.11-slim`
- **Memory:** ~150 MB
- **Restart Policy:** `unless-stopped`

---

### Dashboard Service

**Container:** `ai_vision_dashboard`  
**Port:** 8501  
**Purpose:** Streamlit-based Vision Dashboard

#### Features

- 🏠 Home - Real-time metrics
- 📊 Compare Images - Visual diff analysis
- 📜 History - Cached runs browser
- 🔧 Healing Logs - Vision-based healing explorer
- 📈 Metrics - Performance dashboard

#### Configuration

- **Dockerfile:** `docker/dashboard.Dockerfile`
- **Base Image:** `python:3.11-slim`
- **Memory:** ~200 MB
- **Restart Policy:** `unless-stopped`

---

### Test Runner Service

**Container:** `ai_test_runner`  
**Purpose:** Pytest-based test execution

#### Usage

```bash
# Run all tests
docker-compose run --rm tests

# Run specific test file
docker-compose run --rm tests pytest tests/test_ai_healer.py

# Run with verbose output
docker-compose run --rm tests pytest -v -s
```

#### Configuration

- **Dockerfile:** `docker/test.Dockerfile`
- **Base Image:** `python:3.11-slim`
- **Memory:** ~180 MB
- **Profile:** `test` (on-demand only)

---

## 🛠️ Build & Run

### Build Commands

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api
docker-compose build dashboard
docker-compose build tests

# Rebuild without cache (fresh build)
docker-compose build --no-cache

# Build with progress output
docker-compose build --progress=plain
```

### Run Commands

```bash
# Start all services (detached)
docker-compose up -d

# Start specific service
docker-compose up -d api
docker-compose up -d dashboard

# Start with logs (attached)
docker-compose up

# Run tests (one-time execution)
docker-compose run --rm tests

# View logs
docker-compose logs -f api
docker-compose logs -f dashboard
docker-compose logs --tail=100 api

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Scaling (Advanced)

```bash
# Run multiple API instances
docker-compose up -d --scale api=3

# Load balancer needed for distribution
```

---

## ✅ Verification

### 1. Build Verification

```bash
docker-compose build
```

**Expected:**
- ✅ All 3 services build successfully
- ✅ No errors in output
- ✅ Images tagged correctly

**Check:**
```bash
docker images | grep ai_test_foundation
```

---

### 2. API Container Verification

```bash
docker-compose up -d api
```

**Expected:**
- ✅ Container `ai_locator_api` running
- ✅ Port 8000 accessible
- ✅ Health check passing

**Check:**
```bash
# Container status
docker ps | grep ai_locator_api

# Health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"locator-repair-service","version":"1.0.0"}

# Swagger docs
curl http://localhost:8000/docs
# or open in browser
```

---

### 3. Dashboard Container Verification

```bash
docker-compose up -d dashboard
```

**Expected:**
- ✅ Container `ai_vision_dashboard` running
- ✅ Port 8501 accessible
- ✅ UI loads 5 tabs

**Check:**
```bash
# Container status
docker ps | grep ai_vision_dashboard

# Health endpoint
curl http://localhost:8501/_stcore/health

# Open dashboard in browser
# Navigate to: http://localhost:8501
# Verify all 5 pages load:
# - Home
# - Compare Images
# - History
# - Healing Logs
# - Metrics
```

---

### 4. Test Runner Verification

```bash
docker-compose run --rm tests
```

**Expected:**
- ✅ Tests execute successfully
- ✅ ~60 tests pass
- ✅ Execution time: ~15-20s

**Check:**
```bash
# Run tests and capture output
docker-compose run --rm tests pytest -v

# Expected output:
# ======================== test session starts =========================
# collected 60 items
# ...
# ==================== 60 passed in 15.30s ====================
```

---

### 5. Cross-Container Communication

```bash
# Enter test container
docker-compose run --rm tests bash

# Inside container, test API connectivity
curl http://api:8000/health

# Expected: {"status":"healthy"}
```

**Expected:**
- ✅ Test container can reach API via Docker network
- ✅ DNS resolution works (`api` resolves to API container)

---

### 6. Volume & Cache Verification

```bash
# Check host logs directory
ls -la logs/

# Expected files:
# - healing_log.json
# - vision_cache.json
# - healing_cache.json

# View recent logs
tail -n 10 logs/healing_log.json

# Check for vision-based healings
cat logs/healing_log.json | grep "healing_source.*vision"
```

**Expected:**
- ✅ Logs synchronized between containers and host
- ✅ Cache files updated during test runs
- ✅ Vision healings logged correctly

---

### 7. Performance Check

```bash
docker stats --no-stream
```

**Expected Resource Usage:**

| Container | CPU | Memory | Expected |
|-----------|-----|--------|----------|
| ai_locator_api | <5% | ~150 MB | ✅ |
| ai_vision_dashboard | <10% | ~200 MB | ✅ |
| ai_test_runner | varies | ~180 MB | ✅ |
| **Total** | | **<500 MB** | ✅ |

**Check:**
```bash
# Detailed stats with updates
docker stats

# Press Ctrl+C to exit
```

---

### 8. Clean Down

```bash
# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Remove all (including images)
docker-compose down --rmi all -v
```

**Expected:**
- ✅ All containers stopped
- ✅ Networks removed
- ✅ Volumes removed (if `-v` used)

---

## 🐛 Troubleshooting

### Issue 1: Build Fails

**Error:** `ERROR [internal] load metadata for docker.io/library/python:3.11-slim`

**Solution:**
```bash
# Check Docker daemon is running
docker ps

# Check internet connectivity
ping google.com

# Try with different base image
# Edit Dockerfile: FROM python:3.11-slim -> FROM python:3.11
```

---

### Issue 2: Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# Kill the process or change port in docker-compose.yml:
# ports:
#   - "8001:8000"  # Host:Container
```

---

### Issue 3: API Health Check Fails

**Error:** Health check keeps failing

**Solution:**
```bash
# Check API logs
docker-compose logs api

# Enter container and test manually
docker exec -it ai_locator_api bash
curl http://localhost:8000/health

# Common causes:
# - .env file not mounted correctly
# - Missing API keys
# - Port conflict

# Disable health check temporarily (docker-compose.yml):
# Comment out healthcheck section
```

---

### Issue 4: Dashboard Won't Load

**Error:** `ERR_CONNECTION_REFUSED` on http://localhost:8501

**Solution:**
```bash
# Check container status
docker-compose ps

# Check dashboard logs
docker-compose logs dashboard

# Common causes:
# - Container crashed (check logs)
# - Firewall blocking port 8501
# - Streamlit config issue

# Try accessing directly
docker exec -it ai_vision_dashboard bash
curl http://localhost:8501/_stcore/health
```

---

### Issue 5: Tests Fail in Container

**Error:** Tests pass locally but fail in Docker

**Solution:**
```bash
# Check Python version match
docker-compose run --rm tests python --version

# Check dependencies
docker-compose run --rm tests pip list

# Run tests with verbose output
docker-compose run --rm tests pytest -v -s --tb=long

# Common causes:
# - Missing system dependencies (Playwright browsers)
# - Path issues (working directory)
# - Environment variables not set
```

---

### Issue 6: Volume Not Syncing

**Error:** Changes in `logs/` not visible in container

**Solution:**
```bash
# Check volume mounts
docker inspect ai_locator_api | grep Mounts -A 20

# Test write from container
docker exec -it ai_locator_api bash
echo "test" > /app/logs/test.txt
exit

# Check on host
cat logs/test.txt

# Windows-specific: Enable file sharing in Docker Desktop
# Settings → Resources → File Sharing → Add project folder
```

---

### Issue 7: Slow Performance

**Error:** Containers running slowly

**Solution:**
```bash
# Check resource limits
docker stats

# Increase Docker Desktop memory
# Settings → Resources → Memory → 8 GB

# Optimize images (multi-stage builds)
# Use .dockerignore properly
# Clear unused images/containers
docker system prune -a
```

---

## ⚡ Performance

### Optimization Tips

#### 1. Layer Caching

```dockerfile
# Good: Copy requirements first (cached if unchanged)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Bad: Copy everything first (invalidates cache)
COPY . .
RUN pip install -r requirements.txt
```

#### 2. Multi-Stage Builds

```dockerfile
# Build stage
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
```

#### 3. .dockerignore

Always exclude:
- `venv/`, `__pycache__/`, `.git/`
- Large files not needed in container
- Development files (`.vscode/`, `.idea/`)

#### 4. Image Size

```bash
# Check image sizes
docker images | grep ai_test_foundation

# Target sizes:
# - API: <500 MB
# - Dashboard: <550 MB
# - Tests: <800 MB (includes Playwright)
```

### Performance Benchmarks

| Metric | Target | Typical |
|--------|--------|---------|
| Build Time (all services) | <3 min | 2-2.5 min |
| Startup Time (API) | <5s | 3-4s |
| Startup Time (Dashboard) | <10s | 8-10s |
| Test Execution | <20s | 15-18s |
| Memory (total) | <500 MB | 400-450 MB |

---

## 🚀 Production Deployment

### Environment-Specific Configs

```bash
# Development
docker-compose -f docker-compose.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**docker-compose.prod.yml:**
```yaml
version: '3.8'
services:
  api:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  dashboard:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Security Best Practices

1. **Never bake secrets in images**
   ```bash
   # Bad: COPY .env /app/.env
   # Good: Mount at runtime
   docker run --env-file .env myimage
   ```

2. **Use non-root user**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

3. **Scan images for vulnerabilities**
   ```bash
   docker scan ai_test_foundation:latest
   ```

4. **Use specific image tags**
   ```dockerfile
   # Bad: FROM python:3.11
   # Good: FROM python:3.11.6-slim
   ```

### CI/CD Integration

**GitHub Actions Example:**

```yaml
name: Docker Build & Test

on: [push]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build images
        run: docker-compose build
      
      - name: Start services
        run: docker-compose up -d api dashboard
      
      - name: Run tests
        run: docker-compose run --rm tests
      
      - name: Stop services
        run: docker-compose down
```

---

## 📊 Monitoring

### Container Logs

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 dashboard

# Logs with timestamps
docker-compose logs -t
```

### Health Checks

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Watch health checks
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}"'
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Export to file
docker stats --no-stream > docker-stats.txt
```

---

## 📝 Summary

✅ **Docker Compose** orchestrates 3 services  
✅ **Shared volumes** for logs and reports  
✅ **Docker network** for inter-container communication  
✅ **Health checks** for service monitoring  
✅ **Resource limits** for performance  
✅ **Production-ready** with restart policies

---

**End of Docker Deployment Guide**

*Last Updated: November 12, 2025*  
*Version: 1.0.0*  
*Author: Ram*
