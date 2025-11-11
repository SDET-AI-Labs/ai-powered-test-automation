# 📚 AI-Powered Test Automation - Complete Learning Guide

## Table of Contents
1. [Understanding Errors](#understanding-errors)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Step-by-Step Debugging](#step-by-step-debugging)
4. [AI Healing Workflow](#ai-healing-workflow)
5. [Running Tests Successfully](#running-tests-successfully)
6. [Troubleshooting Tips](#troubleshooting-tips)

---

## 🔍 Understanding Errors

### Error Type 1: Network Timeout

**Error Message:**
```
playwright._impl._errors.TimeoutError: Page.goto: Timeout 30000ms exceeded.
```

**What It Means:**
- Playwright tried to navigate to a URL
- Waited for 30 seconds (30,000 milliseconds)
- The page never finished loading
- Connection timed out

**Breaking Down the Error:**
1. `Page.goto` - The action that failed (navigation)
2. `Timeout 30000ms` - How long it waited
3. `exceeded` - It gave up after timeout

**Root Causes:**
- ❌ Corporate network blocks external websites
- ❌ SSL certificate issues (self-signed certificates)
- ❌ Proxy/firewall intercepted HTTPS requests
- ❌ Website is actually down

**How to Fix:**
```python
# Option 1: Use local HTML content
html_content = """<!DOCTYPE html>..."""
page.set_content(html_content)

# Option 2: Add SSL bypass
browser = p.chromium.launch(
    headless=True,
    args=['--ignore-certificate-errors']
)
context = browser.new_context(ignore_https_errors=True)
page = context.new_page()

# Option 3: Increase timeout and add fallback
try:
    page.goto(url, timeout=15000, wait_until="domcontentloaded")
except Exception:
    # Use local HTML fallback
    page.set_content(html_content)
```

---

### Error Type 2: Module Import Error

**Error Message:**
```
ModuleNotFoundError: No module named 'core'
```

**What It Means:**
- Python can't find the module you're trying to import
- The package structure is incomplete

**Root Causes:**
- ❌ Missing `__init__.py` files in directories
- ❌ Wrong import path
- ❌ Package not in Python path

**How to Fix:**
```python
# Step 1: Add __init__.py to all package directories
# core/__init__.py
"""
core package - AI-powered test automation components
"""
from .ai_healer import AIHealer
__all__ = ["AIHealer"]

# tests/__init__.py
"""
tests package - Test suite for AI-powered test automation
"""

# tests/integration/__init__.py
"""
integration tests package
"""

# Step 2: Verify import paths
from core.ai_healer import AIHealer  # ✅ Correct
# from ai_healer import AIHealer      # ❌ Wrong (missing core)
```

---

### Error Type 3: SSL Certificate Error

**Error Message:**
```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]'))
```

**What It Means:**
- HTTPS connection failed due to untrusted SSL certificate
- Common in corporate networks with proxy/firewall

**How to Fix:**
```python
# For Requests library
import requests
response = requests.post(url, verify=False)  # Disable SSL verification

# For HTTPX (used by Groq)
import httpx
http_client = httpx.Client(verify=False)

# For Playwright
browser = p.chromium.launch(args=['--ignore-certificate-errors'])
context = browser.new_context(ignore_https_errors=True)

# For Selenium
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)
```

---

### Error Type 4: AI Response Formatting Issues

**Error Message:**
```
Unexpected token "`" while parsing css selector "`input#firstname`"
```

**What It Means:**
- AI returned locator wrapped in markdown backticks
- Playwright can't parse it as a valid CSS selector

**How to Fix:**
```python
# Clean AI response in ai_healer.py
new_locator = self.ai.ask(prompt).strip()

# Remove markdown formatting
new_locator = new_locator.strip('`"\'')  # Remove backticks and quotes

# Remove code blocks
if new_locator.startswith('```') and new_locator.endswith('```'):
    new_locator = new_locator[3:-3].strip()

# Take only first line if multi-line response
if '\n' in new_locator:
    new_locator = new_locator.split('\n')[0].strip()
```

---

## 🛠️ Common Issues & Solutions

### Issue 1: Test Can't Find ChromeDriver (Selenium)

**Problem:**
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solution:**
```python
# Install webdriver-manager
pip install webdriver-manager

# Use it in your test
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

**Or just use options (webdriver-manager auto-handles it):**
```python
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)  # Auto-downloads driver
```

---

### Issue 2: External Websites Blocked

**Problem:**
- Corporate network blocks w3schools.com, example.com, etc.
- Tests timeout when trying to navigate

**Solution:**
```python
# Create local HTML test pages
html_content = """
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Test Form</h1>
    <form>
        <input type="text" id="firstname" name="firstname">
        <input type="text" id="lastname" name="lastname">
        <button id="submit-btn">Submit</button>
    </form>
</body>
</html>
"""

# Playwright
page.set_content(html_content)

# Selenium
driver.get("data:text/html;charset=utf-8," + html_content)
```

---

### Issue 3: AI Provider Not Working

**Problem:**
- AI healing fails silently
- No response from AI

**Diagnosis Steps:**
```bash
# Step 1: Check .env file
AI_PROVIDER=openrouter  # or groq, gemini, openai
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Step 2: Test AI gateway directly
python ai_gateway.py

# Step 3: Check specific provider
AI_PROVIDER=groq python ai_gateway.py
AI_PROVIDER=gemini python ai_gateway.py
AI_PROVIDER=openrouter python ai_gateway.py
```

**Solution:**
```python
# In .env
AI_PROVIDER=groq  # Fast and free (default)
GROQ_API_KEY=your_actual_key_here

# Verify in terminal
python ai_gateway.py
# Should output: [INFO] Active AI provider: groq
```

---

### Issue 4: pytest Can't Find Tests

**Problem:**
```bash
collected 0 items / 1 error
ERROR collecting tests/test_ai_healing.py
```

**Solution:**
```bash
# Add __init__.py files to make directories Python packages
touch tests/__init__.py
touch tests/integration/__init__.py
touch core/__init__.py

# Run from project root
cd d:\Yogesh\Testing\Office Work Projects\ai_test_foundation
pytest -s -v tests/
```

---

## 🔧 Step-by-Step Debugging

### Debugging Process

**Step 1: Read the Error Message**
```
Look at the LAST line of the traceback:
- TimeoutError → Network/loading issue
- ModuleNotFoundError → Missing package/import
- SSLError → Certificate issue
- AttributeError → Missing method/property
```

**Step 2: Find the Failing Line**
```
Traceback shows:
tests\test_ai_healing.py:28:
    page.goto(url)

Line 28 in test_ai_healing.py is where it failed
```

**Step 3: Identify the Root Cause**
```
TimeoutError + page.goto = Navigation failed
Possible causes:
1. Network blocked
2. SSL issue
3. Wrong URL
4. Page doesn't exist
```

**Step 4: Apply the Fix**
```python
# Before (fails)
page.goto("https://example.com")

# After (works)
page.set_content(html_content)
```

**Step 5: Verify the Fix**
```bash
pytest -s -v tests/test_ai_healing.py
# Should output: PASSED
```

---

### Debugging Checklist

When a test fails, check these in order:

- [ ] **Is the error in the test file or imported module?**
  - Test file → Fix test logic
  - Imported module → Fix the module

- [ ] **Is it a network/timeout issue?**
  - Use local HTML content
  - Add SSL bypass flags
  - Increase timeout

- [ ] **Is it an import error?**
  - Add `__init__.py` files
  - Check import paths
  - Verify module exists

- [ ] **Is it an AI provider issue?**
  - Test with `python ai_gateway.py`
  - Check API key in `.env`
  - Try different provider

- [ ] **Is it a locator issue?**
  - Verify element exists in page
  - Check HTML structure
  - Test with browser DevTools

---

## 🤖 AI Healing Workflow

### How AI Healing Works

```
┌─────────────────────────────────────────────────────┐
│ 1. Test tries to interact with element             │
│    page.locator("input#wrong_id").click()          │
└─────────────────────────────────────────────────────┘
                       ↓
                    ❌ FAILS
                       ↓
┌─────────────────────────────────────────────────────┐
│ 2. Test catches exception                           │
│    except Exception as e:                           │
│        print(f"Failed: {failed_locator}")          │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 3. Call AI Healer                                   │
│    healer.heal_locator(page, failed_locator,       │
│                       context_hint)                 │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 4. AI Healer extracts page HTML                     │
│    html_content = page.content()                    │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 5. AI Healer builds prompt                          │
│    "This locator failed: input#wrong_id             │
│     Here's the HTML: <html>...                      │
│     Find the first name input field"                │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 6. Send to AI Provider (Groq/OpenRouter/Gemini)    │
│    new_locator = self.ai.ask(prompt)               │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 7. AI analyzes HTML and suggests fix                │
│    Response: "input#firstname"                      │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 8. Clean AI response                                │
│    Remove backticks, quotes, markdown               │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 9. Log the healing attempt                          │
│    Save to logs/healing_log.json                    │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 10. Return healed locator to test                   │
│     return "input#firstname"                        │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ 11. Test retries with healed locator                │
│     page.locator("input#firstname").fill("John")   │
└─────────────────────────────────────────────────────┘
                       ↓
                    ✅ SUCCESS!
```

---

### AI Healing Code Example

```python
# In your test file
def test_ai_healing():
    healer = AIHealer(log_path="logs/healing_log.json")
    page.set_content(html_content)
    
    failed_locator = "input#wrong_id"
    
    try:
        # Try the wrong locator
        page.locator(failed_locator).click(timeout=2000)
    except Exception as e:
        print(f"❌ Failed: {failed_locator}")
        
        # Call AI Healer
        healed_locator = healer.heal_locator(
            page=page,
            failed_locator=failed_locator,
            context_hint="Find the first name input field"
        )
        
        print(f"✨ AI suggested: {healed_locator}")
        
        # Retry with healed locator
        page.locator(healed_locator).fill("John")
        print("✅ Healed successfully!")
```

---

### Healing Log Format

The healing log (`logs/healing_log.json`) records every healing attempt:

```json
{
  "timestamp": "2025-11-11T19:26:12.806430",
  "engine": "Playwright",
  "old_locator": "input#wrong_id",
  "new_locator": "input#fname"
}
```

**Fields:**
- `timestamp` - When the healing happened
- `engine` - Which framework (Playwright/Selenium)
- `old_locator` - The failed locator
- `new_locator` - AI's suggested fix

---

## 🚀 Running Tests Successfully

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with output (see print statements)
pytest -s

# Run verbose (detailed info)
pytest -v

# Run specific test file
pytest tests/test_ai_healing.py

# Run with both output and verbose
pytest -s -v tests/test_ai_healing.py

# Run specific test function
pytest tests/test_ai_healing.py::test_ai_locator_self_healing

# Run tests matching pattern
pytest -k "healing"

# Run with HTML report
pytest --html=report.html
```

---

### Test Flags Explained

| Flag | Meaning | Use When |
|------|---------|----------|
| `-s` | Show print statements | You want to see AI healing messages |
| `-v` | Verbose mode | You want detailed test info |
| `-k` | Filter by keyword | You want to run specific tests |
| `-x` | Stop on first failure | You're debugging |
| `--lf` | Run last failed tests | Re-running after fix |
| `--html` | Generate HTML report | You need visual report |
| `-n auto` | Run parallel (needs pytest-xdist) | Speed up test suite |

---

### Running Tests - Step by Step

**Step 1: Navigate to project directory**
```bash
cd "d:\Yogesh\Testing\Office Work Projects\ai_test_foundation"
```

**Step 2: Activate virtual environment (if needed)**
```bash
# Already activated if you see (venv) in prompt
# If not:
.\venv\Scripts\activate
```

**Step 3: Check your .env configuration**
```bash
# View current provider
type .env | Select-String "AI_PROVIDER"

# Should show:
# AI_PROVIDER=groq  (or openrouter, gemini, openai)
```

**Step 4: Run the test**
```bash
pytest -s -v tests/test_ai_healing.py
```

**Step 5: Check results**
```bash
# Expected output:
# tests/test_ai_healing.py::test_ai_locator_self_healing PASSED
# ✅ = Success
# ❌ = Failure (need to debug)
```

---

### Running Different Test Files

```bash
# Single test (basic healing)
pytest -s -v tests/test_ai_healing.py

# Dual test (Playwright + Selenium)
pytest -s -v tests/test_ai_healing_dual.py

# All healing tests
pytest -s -v tests/ -k "healing"

# Integration tests
pytest -s -v tests/integration/

# All tests in project
pytest -s -v
```

---

## 🔍 Troubleshooting Tips

### Problem: Test Times Out

**Symptoms:**
```
TimeoutError: Page.goto: Timeout 30000ms exceeded
```

**Solutions:**
1. Use local HTML content instead of external URLs
2. Add SSL bypass flags
3. Reduce timeout and add fallback
4. Check network connectivity

**Quick Fix:**
```python
# Replace this:
page.goto("https://example.com")

# With this:
html_content = """<!DOCTYPE html>..."""
page.set_content(html_content)
```

---

### Problem: AI Returns Long Explanation Instead of Locator

**Symptoms:**
```
AI suggested: "Based on the HTML provided, I recommend using..."
```

**Solution:**
```python
# In ai_healer.py, improve the prompt:
prompt = f"""
Suggest ONE working alternative locator (CSS or XPath).
Respond with ONLY the locator string, without any markdown,
backticks, quotes, or explanations.

Example good response: input#firstname
Example bad response: `input#firstname` or "Use input#firstname"
"""
```

---

### Problem: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'core'
```

**Solution:**
```bash
# Add __init__.py files
New-Item -Path "core\__init__.py" -ItemType File
New-Item -Path "tests\__init__.py" -ItemType File
New-Item -Path "tests\integration\__init__.py" -ItemType File
```

---

### Problem: Selenium Can't Find ChromeDriver

**Symptoms:**
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solution:**
```python
# Use webdriver-manager (already installed)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)  # Auto-downloads driver
```

---

### Problem: AI Provider Not Responding

**Symptoms:**
- Test hangs
- No AI response
- Empty healing log

**Diagnosis:**
```bash
# Test AI gateway directly
python ai_gateway.py

# Should show:
# [INFO] Active AI provider: groq
# AI Response: Hello...
```

**Solution:**
```bash
# Check .env file
AI_PROVIDER=groq
GROQ_API_KEY=your_actual_key_here

# Try different provider
AI_PROVIDER=gemini python ai_gateway.py
AI_PROVIDER=openrouter python ai_gateway.py
```

---

### Problem: Test Passes But Nothing Happens

**Symptoms:**
- Test shows PASSED
- But you don't see healing messages
- No output

**Solution:**
```bash
# Always use -s flag to see output
pytest -s -v tests/test_ai_healing.py

# The -s flag shows print statements:
# ✅ Page loaded
# ❌ Playwright failed
# 🤖 Triggering AI-Healer
# ✨ AI suggested: input#fname
```

---

## 📊 Understanding Test Output

### Good Test Output (Success)

```
tests/test_ai_healing.py::test_ai_locator_self_healing 
[INFO] Active AI provider: openrouter

[Test] Creating test page with form elements...
✅ Page loaded (local HTML)

[Initial Failure] Locator failed: input#wrong_id
[Error] Locator.click: Timeout 2000ms exceeded...
[Triggering AI-Healing...]
[AI-Healer] Suggested new locator: input#firstname
[Healed Interaction] Success! Filled the input with 'John'

================================================================================
--- Recent Healing Events ---
{
  "timestamp": "2025-11-11T19:14:22.271762",
  "engine": "Playwright",
  "old_locator": "input#wrong_id",
  "new_locator": "input#firstname"
}
PASSED ✅
```

**What This Means:**
- ✅ AI provider connected (openrouter)
- ✅ Page loaded successfully
- ✅ Failed locator detected correctly
- ✅ AI suggested valid fix
- ✅ Healed interaction worked
- ✅ Logged to healing_log.json
- ✅ Test passed

---

### Bad Test Output (Failure)

```
tests/test_ai_healing.py::test_ai_locator_self_healing 
FAILED ❌

================================= FAILURES =================================
_______________________ test_ai_locator_self_healing _______________________

    def test_ai_locator_self_healing():
>       page.goto("https://example.com")
E       playwright._impl._errors.TimeoutError: Page.goto: Timeout 30000ms exceeded.

tests\test_ai_healing.py:23: TimeoutError
========================= 1 failed in 32.54s =========================
```

**What This Means:**
- ❌ Network timeout (30 seconds)
- ❌ Could not load external URL
- ❌ Test stopped before AI healing could run
- 🔧 Need to fix: Use local HTML content

---

## 📖 Quick Reference

### Most Common Commands

```bash
# Run test with output
pytest -s -v tests/test_ai_healing.py

# Run dual test (Playwright + Selenium)
pytest -s -v tests/test_ai_healing_dual.py

# Test AI gateway
python ai_gateway.py

# Check provider comparison
python compare_providers.py

# Run all tests
pytest -s -v
```

---

### Most Common Fixes

```python
# Fix 1: Network timeout
page.set_content(html_content)  # Instead of page.goto(url)

# Fix 2: SSL errors
browser = p.chromium.launch(args=['--ignore-certificate-errors'])

# Fix 3: Import errors
# Add __init__.py to all package folders

# Fix 4: AI formatting
new_locator = new_locator.strip('`"\'')  # Remove backticks

# Fix 5: Selenium ChromeDriver
from selenium.webdriver.chrome.options import Options
options = Options()
driver = webdriver.Chrome(options=options)  # Auto-downloads driver
```

---

### Provider Priority

1. **Groq** ⚡ - Fastest (0.78s), free, verbose responses
2. **OpenRouter** 🌐 - Best quality (5.09s), free, concise
3. **Gemini** ✅ - Most concise (8.70s), free, brief
4. **OpenAI** 💰 - Good quality (2.97s), paid, balanced

**Recommendation:**
- Use **Groq** for speed (default)
- Use **OpenRouter** for quality
- Switch in `.env`: `AI_PROVIDER=openrouter`

---

## 🎯 Next Steps

### After Mastering Basics

1. **Create custom healing strategies**
   - Add visual validation
   - Implement similarity scoring
   - Add confidence levels

2. **Extend to more frameworks**
   - Puppeteer
   - WebdriverIO
   - Cypress (via API)

3. **Add advanced features**
   - Screenshot comparison
   - Element clustering
   - Pattern learning

4. **Integrate with CI/CD**
   - GitHub Actions
   - Jenkins
   - Azure DevOps

---

## 📝 Summary

**Key Takeaways:**

1. ✅ Always use `-s -v` flags to see test output
2. ✅ Use local HTML to avoid network issues
3. ✅ Add SSL bypass for corporate networks
4. ✅ Add `__init__.py` files for proper package structure
5. ✅ Clean AI responses to remove markdown formatting
6. ✅ Log all healing attempts for debugging
7. ✅ Test AI gateway independently before running tests
8. ✅ Use appropriate AI provider based on needs

**Remember:**
- **Groq** = Speed
- **OpenRouter** = Quality
- **Local HTML** = Reliability
- **Error messages** = Your debugging guide

---

## 🆘 Getting Help

**If stuck:**
1. Check this guide first
2. Read error message carefully
3. Test AI gateway: `python ai_gateway.py`
4. Use local HTML content
5. Add SSL bypass flags
6. Check logs: `logs/healing_log.json`

**Common Error Keywords:**
- `TimeoutError` → Use local HTML
- `ModuleNotFoundError` → Add `__init__.py`
- `SSLError` → Add `verify=False`
- `Unexpected token` → Clean AI response

---

**Happy Testing! 🚀**

---
### Change: Log engine & warning fixes
- Timestamp: 2025-11-11T15:52:02.961181 UTC
- Why: Record engine (Playwright/Selenium) in healing logs and suppress SSL/pytest warnings; ensure tests pass and logs show engine correctly.
- Files changed:
  - core/ai_healer.py
  - ai_gateway.py
  - pytest.ini
  - tests/test_ai_healing.py
  - tests/test_ai_healing_dual.py
  - scripts/append_learning_log.py
- Test result: 2 passed, 4 deselected; warnings suppressed via pytest.ini


---
### Change: Log engine & warning fixes
- Timestamp: 2025-11-11T15:52:24.738983+00:00 UTC
- Why: Record engine (Playwright/Selenium) in healing logs and suppress SSL/pytest warnings; ensure tests pass and logs show engine correctly.
- Files changed:
  - core/ai_healer.py
  - ai_gateway.py
  - pytest.ini
  - tests/test_ai_healing.py
  - tests/test_ai_healing_dual.py
  - scripts/append_learning_log.py
- Test result: 2 passed, 4 deselected; warnings suppressed via pytest.ini

