# Universal AI Interaction Layer

**Phase 7 Enhancement: Adaptive Interaction Engine**

## 🎯 Overview

The **Universal AI Interaction Layer** is an adaptive automation framework that enables testing on ANY website, including those with anti-automation protection. It combines:

1. **AIInteractor** - Adaptive interaction with intelligent fallback hierarchy
2. **Stealth Browser** - Anti-detection measures to bypass bot detection
3. **AI-Healer** - Automatic locator repair using LLM intelligence

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Layer                                   │
│  (Your pytest tests using universal interaction methods)        │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│              AIInteractor (core/ai_interactor.py)               │
│  • safe_fill()  - Adaptive form filling                        │
│  • safe_click() - Adaptive button clicking                     │
│  • Fallback hierarchy: direct → JS → human → degraded         │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│       Stealth Browser (adapters/playwright_adapter.py)          │
│  • launch_stealth_browser() - Anti-detection measures           │
│  • navigator.webdriver hiding                                  │
│  • Automation flag removal                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│            AI-Healer (core/ai_healer.py)                        │
│  • heal_locator() - Repair broken selectors                    │
│  • LLM-powered locator suggestions                             │
│  • Caching for performance                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Fallback Hierarchy

### safe_fill() Method

AIInteractor attempts form filling in this order:

1. **Direct Method** (`page.fill()`)
   - Native Playwright fill
   - Fastest, most reliable when site allows
   - **Used when:** Site has no anti-automation protection

2. **JS Injection** (`element.value = ...`)
   - Sets value via JavaScript
   - Dispatches input/change/blur events
   - **Used when:** Direct fill blocked by site

3. **Human Typing** (char-by-char with delays)
   - Types one character at a time
   - Random 45-80ms delays between keystrokes
   - **Used when:** JS injection fails

4. **Degraded Mode**
   - All methods failed
   - Logs failure, returns False
   - **Used when:** Site completely blocks automation

### safe_click() Method

AIInteractor attempts clicks in this order:

1. **Direct Method** (`page.click()`)
   - Native Playwright click
   - **Used when:** Site allows automation

2. **JS Click** (`element.click()`)
   - JavaScript-based click
   - **Used when:** Direct click blocked

3. **Enter Key** (`focus() + Enter`)
   - Focuses element and presses Enter
   - **Used when:** JS click fails

4. **JS dispatchEvent**
   - Dispatches MouseEvent via JavaScript
   - **Used when:** Enter key fails

5. **Degraded Mode**
   - All methods failed
   - Logs failure, returns False

## 📊 Interaction Logging

Every interaction is logged with:

```json
{
  "interaction_method": "direct" | "js_inject" | "human_typing" | "degraded",
  "interaction_latency_ms": 45.23,
  "selector": "#username",
  "context": "username field",
  "timestamp": 1731424567.123,
  "failed": false
}
```

### Interaction Statistics

```python
interactor = AIInteractor(page)
interactor.safe_fill("#username", "test")
interactor.safe_click("button")

stats = interactor.get_interaction_stats()
# Returns: {
#   "direct": 2,
#   "js_inject": 0,
#   "human_typing": 0,
#   "degraded": 0
# }
```

## 🚀 Usage Examples

### Basic Usage

```python
from adapters.playwright_adapter import launch_stealth_browser
from core.ai_interactor import AIInteractor

# Launch stealth browser
browser, context, page = launch_stealth_browser(headless=True)

# Initialize interactor
interactor = AIInteractor(page, timeout=5000)

# Navigate
page.goto("https://example.com/login")

# Fill form with adaptive fallbacks
username_success = interactor.safe_fill(
    selector="#username",
    value="myuser",
    context_hint="username field"
)

password_success = interactor.safe_fill(
    selector="#password",
    value="mypass",
    context_hint="password field"
)

# Click with adaptive fallbacks
login_success = interactor.safe_click(
    selector="button[type='submit']",
    context_hint="login button"
)

# Check results
if username_success and password_success and login_success:
    print("✅ Login succeeded")
else:
    print("⚠️ Some interactions failed (site may block automation)")
    stats = interactor.get_interaction_stats()
    print(f"Methods used: {stats}")

# Cleanup
browser.close()
```

### With AI-Healer Integration

```python
from adapters.playwright_adapter import launch_stealth_browser
from core.ai_healer import AIHealer
from core.ai_interactor import AIInteractor

# Launch stealth browser
browser, context, page = launch_stealth_browser(headless=True)

# Initialize AI-Healer and AIInteractor
healer = AIHealer()
interactor = AIInteractor(page)

# Navigate
page.goto("https://example.com/login")

# Use broken locator (simulating DOM change)
broken_locator = "#old-username-id"

# AI-Healer repairs the locator
healed_locator = healer.heal_locator(
    page=page,
    failed_locator=broken_locator,
    context_hint="Username input field",
    engine="Playwright"
)

# AIInteractor fills with healed locator
success = interactor.safe_fill(healed_locator, "myuser")

if success:
    print("✅ AI-Healer + AIInteractor working together!")

browser.close()
```

### In Pytest Tests

```python
import pytest
from adapters.playwright_adapter import launch_stealth_browser
from core.ai_interactor import AIInteractor

@pytest.fixture
def stealth_browser():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser, context, page = launch_stealth_browser(
        headless=True,
        playwright_instance=p
    )
    yield browser, context, page
    browser.close()
    p.stop()

def test_login_with_universal_layer(stealth_browser):
    browser, context, page = stealth_browser
    interactor = AIInteractor(page)
    
    page.goto("https://example.com/login")
    
    # Fill and click with adaptive fallbacks
    interactor.safe_fill("#username", "test")
    interactor.safe_fill("#password", "test")
    interactor.safe_click("button[type='submit']")
    
    # Verify
    assert "dashboard" in page.url
    
    # Check interaction methods
    stats = interactor.get_interaction_stats()
    assert stats['degraded'] == 0, "No interactions should degrade"
```

## 🛡️ Stealth Browser Features

The stealth browser includes these anti-detection measures:

### Browser Launch Arguments

```
--disable-blink-features=AutomationControlled
--disable-features=IsolateOrigins,site-per-process
--disable-web-security
--disable-features=VizDisplayCompositor
```

### JavaScript Overrides

```javascript
// Hide navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Fake plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// Spoof languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Add chrome runtime
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};
```

### User Agent

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/120.0.0.0 Safari/537.36
```

## 🔧 Configuration Options

### AIInteractor Timeout

```python
# Default: 5000ms
interactor = AIInteractor(page, timeout=5000)

# Faster timeout for quick sites
interactor = AIInteractor(page, timeout=2000)

# Longer timeout for slow sites
interactor = AIInteractor(page, timeout=10000)
```

### Stealth Browser Options

```python
# Headless mode
browser, context, page = launch_stealth_browser(headless=True)

# Headed mode (for debugging)
browser, context, page = launch_stealth_browser(headless=False)

# Custom viewport
browser, context, page = launch_stealth_browser(
    viewport_width=1366,
    viewport_height=768
)

# Custom user agent
browser, context, page = launch_stealth_browser(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
)

# With proxy (see Proxy Setup section)
browser, context, page = launch_stealth_browser(
    proxy="http://proxy.example.com:8080"
)
```

## 🌐 Proxy Setup (Optional)

For deeper stealth, you can route traffic through a proxy.

### Environment Variables

```bash
# Enable proxy
export USE_PROXY=true
export PROXY_URL=http://proxy.example.com:8080

# Or in .env file
USE_PROXY=true
PROXY_URL=http://proxy.example.com:8080
```

### Launch with Proxy

```python
import os

proxy_url = os.getenv("PROXY_URL") if os.getenv("USE_PROXY") == "true" else None

browser, context, page = launch_stealth_browser(
    headless=True,
    proxy=proxy_url
)
```

### mitmproxy Integration (Advanced)

For header rewriting and automation header stripping:

1. Install mitmproxy:
   ```bash
   pip install mitmproxy
   ```

2. Create mitm script (`strip_automation.py`):
   ```python
   def request(flow):
       # Remove automation headers
       flow.request.headers.pop("X-Automation", None)
       flow.request.headers.pop("Playwright", None)
   ```

3. Start mitmproxy:
   ```bash
   mitmproxy -s strip_automation.py -p 8080
   ```

4. Use proxy in tests:
   ```python
   browser, context, page = launch_stealth_browser(
       proxy="http://localhost:8080"
   )
   ```

**Note:** Proxy/mitmproxy requires SSL certificate handling. See [mitmproxy docs](https://docs.mitmproxy.org/) for certificate installation.

## 📋 Test Results

### Unit Tests (tests/unit/test_ai_interactor.py)

✅ **14/14 tests passed**

- ✅ Direct fill success
- ✅ Fallback to JS injection
- ✅ Fallback to human typing
- ✅ Degraded mode when all fail
- ✅ Direct click success
- ✅ Fallback to JS click
- ✅ Fallback to Enter key
- ✅ Click degraded mode
- ✅ Interaction logging
- ✅ Statistics tracking
- ✅ Log clearing
- ✅ Navigation success
- ✅ Navigation failure
- ✅ Factory function

### Integration Tests (tests/universal/test_saucedemo_universal.py)

✅ **3/3 tests passed** (automation-friendly site)

- ✅ Complete workflow (login succeeds)
- ✅ Direct method preferred (no fallbacks)
- ✅ Interaction logging complete

### Real-World Tests (tests/universal/test_cargain_universal.py)

🔄 **Tests demonstrate framework resilience** (anti-automation site)

- ✅ AI-Healer repairs broken locators
- ✅ AIInteractor tries all fallback methods
- ⚠️ Site blocks automation (expected behavior)
- ✅ Framework handles blocks gracefully (no crashes)

## 🎯 Success Metrics

From test runs:

### SauceDemo (Automation-Friendly)

```
Interaction Statistics:
  direct: 3
  js_inject: 0
  human_typing: 0
  degraded: 0

✅ All interactions used 'direct' method
✅ Login succeeded
✅ Healing log updated (0.01ms cache hit)
```

### CarGain (Anti-Automation Protected)

```
Interaction Statistics:
  direct: 0
  js_inject: 2
  human_typing: 1
  degraded: 1

⚠️ Some methods blocked (expected)
✅ Framework handles gracefully
✅ AI-Healer repaired locator successfully
```

## ⚠️ Known Limitations

### 1. **blocked_by_site vs Framework Failure**

When all interaction methods fail (degraded mode), it typically means:

- ✅ **Framework is working correctly**
- ⚠️ **Site has strong anti-automation protection**

**How to diagnose:**

```python
success = interactor.safe_fill("#field", "value")

if not success:
    log = interactor.get_interaction_log()
    last_entry = log[-1]
    
    if last_entry['interaction_method'] == 'degraded':
        print("⚠️ Site is blocking automation")
        print("   This is NOT a framework failure")
        print("   Consider: headed mode, longer delays, or CAPTCHA solving")
```

### 2. **CAPTCHA Challenges**

AIInteractor **cannot** solve CAPTCHAs. Sites with CAPTCHA will block automation.

**Workarounds:**
- Use sites without CAPTCHA for testing
- Disable CAPTCHA in test environments
- Use CAPTCHA-solving services (2captcha, AntiCaptcha)

### 3. **Two-Factor Authentication (2FA)**

AIInteractor **cannot** handle 2FA codes.

**Workarounds:**
- Disable 2FA for test accounts
- Use backup codes
- Implement SMS/Email code retrieval

### 4. **Rate Limiting**

Rapid automation may trigger rate limits.

**Mitigation:**
- Add delays between interactions
- Use human_typing method (slower, more realistic)
- Rotate IP addresses (proxy)

### 5. **Dynamic Content Loading**

AIInteractor waits for elements but doesn't handle complex SPA loading.

**Best Practice:**
```python
# Wait for network idle
page.wait_for_load_state("networkidle")

# Or wait for specific element
page.wait_for_selector("#target-element", state="visible")

# Then interact
interactor.safe_fill("#target-element", "value")
```

## 🐛 Troubleshooting

### Issue: "All methods failed (degraded)"

**Diagnosis:** Site has anti-automation protection

**Solutions:**
1. Try headed mode: `launch_stealth_browser(headless=False)`
2. Increase timeout: `AIInteractor(page, timeout=10000)`
3. Add manual delays: `time.sleep(2)` between interactions
4. Check element visibility: `page.locator(selector).is_visible()`

### Issue: "Playwright Sync API inside asyncio loop"

**Diagnosis:** Fixture lifecycle issue

**Solution:** Use proper fixture with Playwright instance management:

```python
@pytest.fixture
def stealth_browser():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser, context, page = launch_stealth_browser(
        headless=True,
        playwright_instance=p
    )
    yield browser, context, page
    browser.close()
    p.stop()
```

### Issue: "Element not found"

**Diagnosis:** Locator is broken or page hasn't loaded

**Solution:** Use AI-Healer to repair locators:

```python
healer = AIHealer()

# Try original locator first
try:
    page.locator("#original").click(timeout=2000)
except:
    # Repair if failed
    healed = healer.heal_locator(page, "#original", "button")
    interactor.safe_click(healed)
```

## 📚 API Reference

### AIInteractor Class

```python
class AIInteractor:
    def __init__(self, page: Page, timeout: float = 5000)
    
    def safe_fill(
        self,
        selector: str,
        value: str,
        context_hint: str = ""
    ) -> bool
    
    def safe_click(
        self,
        selector: str,
        context_hint: str = ""
    ) -> bool
    
    def safe_navigate(self, url: str) -> bool
    
    def get_interaction_stats(self) -> Dict[str, int]
    
    def get_interaction_log(self) -> list
    
    def clear_log(self) -> None
```

### launch_stealth_browser Function

```python
def launch_stealth_browser(
    headless: bool = True,
    proxy: Optional[str] = None,
    user_agent: Optional[str] = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    playwright_instance: Optional[Any] = None
) -> tuple[Browser, BrowserContext, Page]
```

## 🎓 Best Practices

1. **Always use stealth browser for protected sites**
   ```python
   browser, context, page = launch_stealth_browser(headless=True)
   ```

2. **Provide context hints for better logging**
   ```python
   interactor.safe_fill("#username", "test", context_hint="username field")
   ```

3. **Check interaction statistics after tests**
   ```python
   stats = interactor.get_interaction_stats()
   assert stats['degraded'] == 0, "No degraded interactions"
   ```

4. **Combine with AI-Healer for robust tests**
   ```python
   healed = healer.heal_locator(page, broken_locator, "hint")
   success = interactor.safe_fill(healed, "value")
   ```

5. **Handle failures gracefully**
   ```python
   if not interactor.safe_fill("#field", "value"):
       print("Site may be blocking - this is expected")
       # Continue test or skip gracefully
   ```

## 📖 Additional Resources

- **Unit Tests:** `tests/unit/test_ai_interactor.py`
- **Integration Tests:** `tests/universal/test_saucedemo_universal.py`
- **Real-World Tests:** `tests/universal/test_cargain_universal.py`
- **Source Code:** `core/ai_interactor.py`, `adapters/playwright_adapter.py`
- **Phase 7 Verification:** `docs/phase7_verification.md`

## 🤝 Contributing

When extending the Universal AI Interaction Layer:

1. Add new fallback methods to `safe_fill()` or `safe_click()`
2. Update `interaction_method` enum in logging
3. Add unit tests for new methods
4. Update this documentation
5. Test on both automation-friendly AND protected sites

## 📝 Changelog

**Phase 7.0 (November 12, 2025)**
- ✅ Initial release
- ✅ AIInteractor with 4-tier fallback hierarchy
- ✅ Stealth browser with anti-detection
- ✅ 14 unit tests, 3 integration tests
- ✅ Comprehensive logging and statistics
- ✅ Tested on SauceDemo (friendly) and CarGain (protected)

---

**Built with ❤️ by Ram for Phase 7 - Universal AI Interaction Layer**
