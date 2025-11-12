# 🌐 Locator Repair REST API

Universal AI-powered locator repair microservice with REST API.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn requests
```

### 2. Start Server
```bash
python -m services.locator_repair.api
```

Server runs at: **http://localhost:8000**

### 3. View API Docs
Open: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### `POST /api/repair`
Repair a broken locator

**Request**:
```json
{
  "framework": "playwright",
  "page_source": "<html>...</html>",
  "failed_locator": "button#wrong",
  "context_hint": "Submit button"
}
```

**Response**:
```json
{
  "success": true,
  "repaired_locator": "button#submit-btn"
}
```

### `GET /health`
Health check

### `GET /api/repairs/recent`
Get recent repair history

### `GET /api/stats`
Get service statistics

---

## 💻 Usage

### Python Client
```python
from services.locator_repair.client import LocatorRepairClient

client = LocatorRepairClient("http://localhost:8000")
result = client.repair_locator(
    framework="playwright",
    page_source=page_source,
    failed_locator="button#wrong"
)
```

### JavaScript/TypeScript
```javascript
const response = await fetch('http://localhost:8000/api/repair', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    framework: 'playwright',
    page_source: pageSource,
    failed_locator: 'button#wrong'
  })
});
const result = await response.json();
```

### cURL
```bash
curl -X POST http://localhost:8000/api/repair \
  -H "Content-Type: application/json" \
  -d '{"framework":"playwright","page_source":"<html>...</html>","failed_locator":"button#wrong"}'
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t locator-repair-service .

# Run
docker run -d -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  locator-repair-service
```

---

## 📚 Documentation

- **API Quick Start**: `docs/API_QUICK_START.md`
- **Full Architecture**: `docs/MICROSERVICES_ARCHITECTURE.md`
- **Implementation Summary**: `docs/REST_API_SUMMARY.md`

---

## ✨ Features

- ✅ FastAPI with auto-generated docs
- ✅ Pydantic data validation
- ✅ CORS support
- ✅ Health checks
- ✅ Statistics tracking
- ✅ Multiple AI providers (Groq, OpenAI, Gemini, OpenRouter)
- ✅ Language-agnostic (HTTP REST API)

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `AI_PROVIDER` | AI provider | `groq` |

---

## 📊 Service Architecture

```
Client (ANY language)
    ↓ HTTP Request
FastAPI Server (this service)
    ↓ Function Call
LocatorRepairService
    ↓ API Call
AI Provider (Groq/OpenAI/etc.)
```

---

**Start Now**: `python -m services.locator_repair.api`
