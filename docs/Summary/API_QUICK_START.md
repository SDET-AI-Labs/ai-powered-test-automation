# 🚀 REST API Quick Start Guide

## Overview

This guide helps you quickly start using the **Locator Repair Microservice** REST API.

---

## 1. Installation

### Install API Dependencies

```bash
pip install fastapi uvicorn requests
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 2. Start the API Server

### Development Mode (with auto-reload)

```bash
python -m services.locator_repair.api
```

Server will start at: **http://localhost:8000**

### Production Mode

```bash
uvicorn services.locator_repair.api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 3. Test the API

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "locator-repair-service",
  "version": "1.0.0",
  "timestamp": "2025-06-15T10:30:00Z"
}
```

### Repair a Locator

```bash
curl -X POST http://localhost:8000/api/repair \
  -H "Content-Type: application/json" \
  -d '{
    "framework": "playwright",
    "page_source": "<html><body><button id=\"submit-btn\">Submit</button></body></html>",
    "failed_locator": "button#wrong-id",
    "context_hint": "Submit button"
  }'
```

Response:
```json
{
  "success": true,
  "original_locator": "button#wrong-id",
  "repaired_locator": "button#submit-btn",
  "framework": "playwright",
  "confidence": 0.95,
  "strategy": "ai_analysis",
  "timestamp": "2025-06-15T10:30:05Z"
}
```

---

## 4. Use the Python Client SDK

### Basic Usage

```python
from services.locator_repair.client import LocatorRepairClient

# Create client
client = LocatorRepairClient("http://localhost:8000")

# Repair locator
result = client.repair_locator(
    framework="playwright",
    page_source=page.content(),
    failed_locator="button#wrong",
    context_hint="Submit button"
)

if result["success"]:
    repaired = result["repaired_locator"]
    print(f"Use this: {repaired}")
```

### With SmartLocator (Remote Mode)

```python
from services.locator_repair.client import RemoteRepairService
from core.smart_locator import SmartLocator, PlaywrightAdapter

# Use remote API instead of local service
repair_service = RemoteRepairService(api_url="http://localhost:8000")

# Create SmartLocator with remote service
adapter = PlaywrightAdapter(page)
locator = SmartLocator(
    "button#wrong",
    adapter,
    repair_service=repair_service
)

# Auto-healing now uses API!
locator.click()
```

---

## 5. API Documentation

Open your browser: **http://localhost:8000/docs**

Interactive Swagger UI with:
- ✅ All endpoints
- ✅ Request/response schemas
- ✅ Try it out feature
- ✅ Examples

Alternative ReDoc: **http://localhost:8000/redoc**

---

## 6. Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/repair` | Repair a broken locator |
| GET | `/api/repairs/recent` | Get recent repair history |
| GET | `/api/stats` | Get service statistics |

---

## 7. Integration Examples

### JavaScript/TypeScript

```javascript
async function repairLocator(failedLocator, pageSource) {
  const response = await fetch('http://localhost:8000/api/repair', {
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
  
  if (result.success) {
    return result.repaired_locator;
  } else {
    throw new Error('Repair failed');
  }
}

// Usage in Playwright test
test('auto-heal broken locator', async ({ page }) => {
  await page.goto('https://example.com');
  
  try {
    await page.locator('button#wrong').click();
  } catch (error) {
    // Repair the locator
    const pageSource = await page.content();
    const repairedLocator = await repairLocator('button#wrong', pageSource);
    
    // Retry with repaired locator
    await page.locator(repairedLocator).click();
  }
});
```

### Java

```java
import java.net.http.*;
import java.net.URI;
import com.google.gson.*;

public class LocatorRepairClient {
    private static final String API_URL = "http://localhost:8000";
    private final HttpClient client;
    private final Gson gson;
    
    public LocatorRepairClient() {
        this.client = HttpClient.newHttpClient();
        this.gson = new Gson();
    }
    
    public String repairLocator(String framework, String pageSource, 
                                String failedLocator, String contextHint) 
            throws Exception {
        
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("framework", framework);
        requestBody.addProperty("page_source", pageSource);
        requestBody.addProperty("failed_locator", failedLocator);
        requestBody.addProperty("context_hint", contextHint);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/api/repair"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(gson.toJson(requestBody)))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JsonObject result = gson.fromJson(response.body(), JsonObject.class);
        
        if (result.get("success").getAsBoolean()) {
            return result.get("repaired_locator").getAsString();
        } else {
            throw new Exception("Repair failed");
        }
    }
}

// Usage in Selenium test
public class TestExample {
    private WebDriver driver;
    private LocatorRepairClient repairClient;
    
    @Test
    public void testAutoHeal() {
        driver.get("https://example.com");
        
        try {
            driver.findElement(By.cssSelector("button#wrong")).click();
        } catch (NoSuchElementException e) {
            // Repair the locator
            String pageSource = driver.getPageSource();
            String repaired = repairClient.repairLocator(
                "selenium", pageSource, "button#wrong", "Submit button"
            );
            
            // Retry with repaired locator
            driver.findElement(By.cssSelector(repaired)).click();
        }
    }
}
```

### C#

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class LocatorRepairClient
{
    private readonly HttpClient _client;
    private readonly string _apiUrl;

    public LocatorRepairClient(string apiUrl = "http://localhost:8000")
    {
        _client = new HttpClient();
        _apiUrl = apiUrl;
    }

    public async Task<string> RepairLocatorAsync(
        string framework, 
        string pageSource, 
        string failedLocator, 
        string contextHint)
    {
        var requestBody = new
        {
            framework = framework,
            page_source = pageSource,
            failed_locator = failedLocator,
            context_hint = contextHint
        };

        var json = JsonSerializer.Serialize(requestBody);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _client.PostAsync($"{_apiUrl}/api/repair", content);
        response.EnsureSuccessStatusCode();

        var responseBody = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<JsonElement>(responseBody);

        if (result.GetProperty("success").GetBoolean())
        {
            return result.GetProperty("repaired_locator").GetString();
        }
        else
        {
            throw new Exception("Repair failed");
        }
    }
}

// Usage in Selenium test
[Test]
public async Task TestAutoHeal()
{
    var repairClient = new LocatorRepairClient();
    
    driver.Navigate().GoToUrl("https://example.com");
    
    try
    {
        driver.FindElement(By.CssSelector("button#wrong")).Click();
    }
    catch (NoSuchElementException)
    {
        // Repair the locator
        var pageSource = driver.PageSource;
        var repaired = await repairClient.RepairLocatorAsync(
            "selenium", pageSource, "button#wrong", "Submit button"
        );
        
        // Retry with repaired locator
        driver.FindElement(By.CssSelector(repaired)).Click();
    }
}
```

---

## 8. Docker Deployment

### Build Image

```bash
docker build -t locator-repair-service .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_api_key \
  --name repair-service \
  locator-repair-service
```

### Test

```bash
curl http://localhost:8000/health
```

---

## 9. Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (fastest) | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `GEMINI_API_KEY` | Gemini API key | - |
| `AI_PROVIDER` | AI provider to use | `groq` |

Set environment variables:

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_key"

# Linux/Mac
export GROQ_API_KEY="your_key"

# .env file (recommended)
echo "GROQ_API_KEY=your_key" >> .env
```

---

## 10. Monitoring

### View Logs

```bash
# Development mode
# Logs appear in console

# Production mode
uvicorn services.locator_repair.api:app --log-config logging.ini
```

### Check Statistics

```bash
curl http://localhost:8000/api/stats
```

Response:
```json
{
  "total_repairs": 150,
  "successful_repairs": 142,
  "failed_repairs": 8,
  "success_rate": 0.9467,
  "frameworks": {
    "playwright": 80,
    "selenium": 70
  },
  "avg_response_time_ms": 245.6
}
```

---

## 11. Troubleshooting

### Server won't start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install fastapi uvicorn
```

### API returns 500 error

**Problem**: AI provider API key missing

**Solution**:
```bash
$env:GROQ_API_KEY="your_key"  # Windows
export GROQ_API_KEY="your_key"  # Linux/Mac
```

### Slow response times

**Problem**: AI provider is slow

**Solution**: Use Groq (fastest provider)
```bash
$env:AI_PROVIDER="groq"
```

---

## 12. Next Steps

1. ✅ Read full architecture: `docs/MICROSERVICES_ARCHITECTURE.md`
2. ⏳ Deploy to production (Docker/K8s)
3. ⏳ Add authentication (API keys)
4. ⏳ Set up monitoring (Prometheus/Grafana)
5. ⏳ Scale horizontally (multiple instances)

---

## Support

- 📚 API Docs: http://localhost:8000/docs
- 🏗️ Architecture: `docs/MICROSERVICES_ARCHITECTURE.md`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Happy Testing! 🚀**
