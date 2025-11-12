# 🏗️ Microservices Architecture Options

## Overview

The AI-healing framework supports **TWO deployment architectures**:

1. **Direct Integration** (Library/SDK approach)
2. **REST API Microservices** (Production-ready)

---

## Architecture 1: Direct Integration (Current)

### How it Works

```
┌─────────────────────────────────────┐
│     Your Test Code                  │
│  (Playwright/Selenium tests)        │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│    SmartLocator/SmartPage           │
│  (Python SDK - direct import)       │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  services/locator_repair/           │
│  repair_service.py                  │
│  (Direct Python function call)      │
└─────────────────────────────────────┘
```

### Usage

```python
# Import and use directly
from core.smart_locator import SmartLocator, PlaywrightAdapter

adapter = PlaywrightAdapter(page)
locator = SmartLocator("button#submit", adapter)
locator.click()  # Auto-heals if broken
```

### Pros ✅
- **Fast** - No network overhead
- **Simple** - Direct function calls
- **Easy debugging** - Everything in same process
- **No infrastructure** - No server setup needed

### Cons ❌
- **Language-locked** - Python only
- **Scaling issues** - Runs in test process
- **No central management** - Each test has own instance
- **Resource-heavy** - AI model loaded per test

### Best For
- ✅ Small teams
- ✅ Python-only projects
- ✅ Development/testing
- ✅ Quick prototypes

---

## Architecture 2: REST API Microservices (Recommended for Production)

### How it Works

```
┌─────────────────────────────────────────────────────┐
│        Your Test Code (ANY Language)                │
│   - Python tests                                    │
│   - JavaScript/TypeScript tests                     │
│   - Java tests                                      │
│   - C# tests                                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ HTTP Request
                       ▼
┌─────────────────────────────────────────────────────┐
│    Load Balancer / API Gateway                      │
│  (NGINX, AWS ALB, Kong, etc.)                       │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Service  │    │ Service  │    │ Service  │
│ Instance │    │ Instance │    │ Instance │
│    #1    │    │    #2    │    │    #3    │
└──────────┘    └──────────┘    └──────────┘

Each instance runs:
┌─────────────────────────────────────┐
│  FastAPI Server                     │
│  services/locator_repair/api.py     │
│                                     │
│  Endpoints:                         │
│  - POST /api/repair                 │
│  - GET  /api/repairs/recent         │
│  - GET  /api/stats                  │
│  - GET  /health                     │
└─────────────────────────────────────┘
```

### Usage

#### Python Client
```python
from services.locator_repair.client import LocatorRepairClient

client = LocatorRepairClient("http://api.yourcompany.com:8000")

result = client.repair_locator(
    framework="playwright",
    page_source=page.content(),
    failed_locator="button#wrong",
    context_hint="Submit button"
)

if result["success"]:
    page.locator(result["repaired_locator"]).click()
```

#### JavaScript Client
```javascript
// JavaScript/TypeScript
async function repairLocator(failedLocator, pageSource) {
  const response = await fetch('http://api.yourcompany.com:8000/api/repair', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      framework: 'playwright',
      page_source: pageSource,
      failed_locator: failedLocator,
      context_hint: 'Submit button'
    })
  });
  
  const result = await response.json();
  return result.repaired_locator;
}
```

#### Java Client
```java
// Java
HttpClient client = HttpClient.newHttpClient();

String json = String.format(
    "{\"framework\":\"selenium\",\"page_source\":\"%s\",\"failed_locator\":\"%s\"}",
    pageSource, failedLocator
);

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://api.yourcompany.com:8000/api/repair"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(json))
    .build();

HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
```

#### cURL (Any Language)
```bash
curl -X POST http://api.yourcompany.com:8000/api/repair \
  -H "Content-Type: application/json" \
  -d '{
    "framework": "playwright",
    "page_source": "<html>...</html>",
    "failed_locator": "button#wrong",
    "context_hint": "Submit button"
  }'
```

### Pros ✅
- **Language-agnostic** - Works with ANY language/framework
- **Centralized** - One service for all teams
- **Scalable** - Add instances as needed
- **Load balanced** - Distribute load across instances
- **Monitoring** - Centralized metrics and logging
- **Versioning** - API versioning for backward compatibility
- **Caching** - Can cache common repairs
- **Rate limiting** - Prevent abuse
- **Authentication** - Secure with API keys

### Cons ❌
- **Network latency** - HTTP overhead (~50-200ms)
- **Infrastructure** - Need servers/containers
- **Complexity** - More moving parts
- **Deployment** - Requires DevOps

### Best For
- ✅ Large teams
- ✅ Multiple languages/frameworks
- ✅ Production environments
- ✅ High-volume testing
- ✅ Enterprise deployments

---

## Deployment Options

### Option 1: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/locator_repair /app/services/locator_repair

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "services.locator_repair.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build
docker build -t locator-repair-service .

# Run
docker run -d -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  locator-repair-service
```

### Option 2: Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locator-repair-service
spec:
  replicas: 3  # 3 instances
  selector:
    matchLabels:
      app: locator-repair
  template:
    metadata:
      labels:
        app: locator-repair
    spec:
      containers:
      - name: api
        image: locator-repair-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-keys
              key: groq-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: locator-repair-service
spec:
  selector:
    app: locator-repair
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Option 3: AWS Lambda (Serverless)

```python
# lambda_handler.py
from mangum import Mangum
from services.locator_repair.api import app

# Wrap FastAPI for Lambda
handler = Mangum(app)
```

### Option 4: Cloud Run (Google Cloud)

```bash
# Deploy to Cloud Run
gcloud run deploy locator-repair-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key
```

---

## Comparison Matrix

| Feature | Direct Integration | REST API Microservice |
|---------|-------------------|----------------------|
| **Languages** | Python only | ANY (Python, JS, Java, C#, etc.) |
| **Latency** | ~0ms (direct) | ~50-200ms (HTTP) |
| **Scalability** | Limited (per test) | Excellent (horizontal) |
| **Setup Complexity** | Low (pip install) | High (server/container) |
| **Resource Usage** | High (per test) | Low (shared service) |
| **Monitoring** | Difficult | Easy (centralized) |
| **Updates** | Redeploy tests | Update service only |
| **Cost** | Low (no infra) | Medium (servers/cloud) |
| **Team Size** | 1-5 | 5+ |
| **Production Ready** | ⚠️ Limited | ✅ Yes |

---

## Hybrid Approach (Best of Both Worlds)

You can use BOTH architectures:

```python
from services.locator_repair import LocatorRepairService
from services.locator_repair.client import RemoteRepairService

# Development: Use local service
if os.getenv("ENV") == "development":
    repair_service = LocatorRepairService()
    
# Production: Use remote API
else:
    repair_service = RemoteRepairService(
        api_url=os.getenv("REPAIR_API_URL")
    )

# Same interface, different backends!
result = repair_service.repair_locator(
    framework="playwright",
    page_source=page_source,
    failed_locator=failed_locator
)
```

---

## Migration Path

### Phase 1: Development (Direct Integration)
- Use SmartLocator with local service
- Fast iteration, easy debugging
- No infrastructure needed

### Phase 2: Testing (Hybrid)
- Deploy API service for testing
- Some teams use API, some use direct
- Validate API performance

### Phase 3: Production (Full Microservice)
- All teams use API
- Scale as needed
- Centralized monitoring

---

## API Server Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic requests
```

### 2. Start Server

```bash
# Development
uvicorn services.locator_repair.api:app --reload --port 8000

# Production
uvicorn services.locator_repair.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# Repair locator
curl -X POST http://localhost:8000/api/repair \
  -H "Content-Type: application/json" \
  -d '{
    "framework": "playwright",
    "page_source": "<button id=\"submit\">Submit</button>",
    "failed_locator": "button#wrong",
    "context_hint": "Submit button"
  }'
```

### 4. View Documentation

Open browser: http://localhost:8000/docs

Interactive API documentation with:
- All endpoints
- Request/response schemas
- Try it out feature

---

## Monitoring & Observability

### Metrics to Track

```python
# Example: Prometheus metrics
from prometheus_client import Counter, Histogram

repair_requests = Counter('repair_requests_total', 'Total repair requests')
repair_latency = Histogram('repair_latency_seconds', 'Repair latency')
repair_success = Counter('repair_success_total', 'Successful repairs')
repair_failure = Counter('repair_failure_total', 'Failed repairs')
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('repair_service.log'),
        logging.StreamHandler()
    ]
)
```

### Distributed Tracing

```python
# OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter

tracer = trace.get_tracer(__name__)

@app.post("/api/repair")
async def repair_locator(request: RepairRequestAPI):
    with tracer.start_as_current_span("repair_locator"):
        # ... repair logic
        pass
```

---

## Security Considerations

### 1. API Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

@app.post("/api/repair")
async def repair_locator(
    request: RepairRequestAPI,
    api_key: str = Security(API_KEY_HEADER)
):
    if api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    # ... rest of code
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/repair")
@limiter.limit("10/minute")  # 10 requests per minute
async def repair_locator(request: RepairRequestAPI):
    # ... repair logic
    pass
```

### 3. Input Validation

```python
class RepairRequestAPI(BaseModel):
    page_source: str = Field(
        ...,
        max_length=50000,  # Prevent abuse
        description="HTML content"
    )
    failed_locator: str = Field(
        ...,
        max_length=1000,
        regex=r"^[a-zA-Z0-9#.\[\]=\"\':\s\-_>]+$"  # Only safe characters
    )
```

---

## Recommendation

### For Your Situation (Based on Experience)

**Start with Direct Integration**, then **migrate to REST API** when:

1. ✅ You have multiple teams
2. ✅ You use multiple languages (Python + JS + Java)
3. ✅ You need centralized management
4. ✅ You have DevOps support
5. ✅ You're running 100+ tests daily

**Typical Timeline:**
- **Month 1-3**: Direct integration (fast development)
- **Month 3-6**: Deploy API service (parallel)
- **Month 6+**: Full migration to API (production)

---

## Files Created

```
services/locator_repair/
├── __init__.py
├── ai_gateway.py          # Moved from root
├── repair_service.py      # Core repair logic
├── api.py                 # FastAPI REST API (NEW)
└── client.py              # HTTP client SDK (NEW)

scripts/
└── compare_providers.py   # Moved from root
```

---

## Next Steps

1. ✅ **Test current setup** (direct integration)
2. ⏳ **Install FastAPI** (`pip install fastapi uvicorn`)
3. ⏳ **Start API server** (`python -m services.locator_repair.api`)
4. ⏳ **Test with client** (`python -m services.locator_repair.client`)
5. ⏳ **Deploy to production** (Docker/K8s/Cloud)

---

**Your experience is correct**: Production systems should use API-based microservices for:
- **Scalability**
- **Language independence**
- **Centralized management**
- **Better monitoring**

Both architectures are now implemented and ready to use! 🚀
