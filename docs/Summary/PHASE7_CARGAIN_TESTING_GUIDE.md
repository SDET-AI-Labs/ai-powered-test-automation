# Phase 7: Real-World Live Site Testing Guide

**CarGain Login Page Testing with AI-Healer + VisionAnalyzer**

Phase 7: Real-World Testing  
Target Site: https://cargainqa.rategain.com/#/Login  
Author: Ram  
Date: November 12, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Objectives](#test-objectives)
3. [Target Site Analysis](#target-site-analysis)
4. [Test Cases](#test-cases)
5. [Setup Instructions](#setup-instructions)
6. [Running Tests](#running-tests)
7. [Expected Results](#expected-results)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Phase 7 validates the **AI-powered test automation framework** against a **real-world production-like application**. We're testing the CarGain QA login page, which uses:

- **Front-end**: Angular/React hybrid (Webpack bundle)
- **DOM Type**: Dynamic + Shadow DOM elements
- **Locator Stability**: Low (React component IDs change frequently)
- **Automation Difficulty**: Moderate to High

This is the **perfect use case** for AI-Healer and SmartLocator, as traditional automation would frequently break due to dynamic locator changes.

---

## 🎯 Test Objectives

We're validating 5 core capabilities:

1. **Baseline Functionality** - Framework works without healing
2. **AI-Healer Auto-Repair** - Broken locators are automatically fixed
3. **Vision Validation** - Screenshot comparison detects visual changes
4. **Error Handling** - Vision detects new error messages
5. **Docker Integration** - Everything works in containerized environment

---

## 🔍 Target Site Analysis

### Page Structure

After loading https://cargainqa.rategain.com/#/Login, you'll find:

| Element | Typical Locator | Stability |
|---------|----------------|-----------|
| **Username Field** | `input[formcontrolname='username']` | Medium |
| **Password Field** | `input[formcontrolname='password']` | Medium |
| **Login Button** | `button[type='submit']` | Low (React-generated) |
| **Error Toast** | `.toast-message` | Dynamic (appears on error) |
| **Remember Me** | Checkbox with dynamic label | Low |

### Why This Site?

✅ **Dynamic Rendering** - Angular uses client-side rendering, locators change  
✅ **Real-World Complexity** - Similar to production applications  
✅ **Perfect for AI-Healer** - Frequent locator changes trigger auto-repair  
✅ **Vision Testing** - Error messages and UI changes are visual  

---

## 🧪 Test Cases

### Test Case #1: Valid Login (Baseline)

**Purpose**: Verify framework works without healing

**Steps**:
1. Navigate to login page
2. Locate username/password fields using standard locators
3. Enter valid credentials
4. Click login button
5. Capture baseline screenshot
6. Verify successful login or redirect

**Expected Result**:  
✅ Test passes without AI-Healer intervention  
✅ Baseline screenshot saved to `reports/screenshots/cargain/baseline_login.png`

**Command**:
```bash
pytest -v tests/test_cargain_login.py::test_valid_login_baseline
```

---

### Test Case #2: Broken Locator → AI-Healer Recovery

**Purpose**: Validate AI-Healer auto-repair capability

**Steps**:
1. Navigate to login page
2. Use intentionally broken locator: `#username-field-broken-id-12345`
3. Trigger AI-Healer to repair locator
4. Verify healed locator works
5. Check `logs/healing_log.json` for `healing_source: "ai"`
6. Verify latency_ms is logged

**Expected Result**:  
✅ AI-Healer repairs locator (e.g., `input[placeholder='Username']`)  
✅ Healing logged with source, latency, and confidence  
✅ Test continues successfully with healed locator

**Healing Log Example**:
```json
{
  "timestamp": "2025-11-12T14:05:33.456",
  "engine": "playwright",
  "old_locator": "#username-field-broken-id-12345",
  "new_locator": "input[formcontrolname='username']",
  "healing_source": "ai",
  "latency_ms": 327.2,
  "confidence": 0.96
}
```

**Command**:
```bash
pytest -v tests/test_cargain_login.py::test_broken_locator_ai_healing
```

---

### Test Case #3: Vision Validation on Login Button

**Purpose**: Verify VisionAnalyzer screenshot comparison

**Steps**:
1. Navigate to login page
2. Capture baseline screenshot
3. Simulate visual change (5% zoom: `scale(1.05)`)
4. Capture modified screenshot
5. Run `VisionAnalyzer.compare_images()`
6. Verify diff detection (expected: 5-10% difference)
7. Check LLM explanation

**Expected Result**:  
✅ VisionAnalyzer detects visual difference  
✅ Diff percentage reported (5-10%)  
✅ AI explanation: "Login button appears slightly larger due to zoom"  
✅ Diff overlay image saved to `reports/`

**Vision Cache Example**:
```json
{
  "description": "Login button moved slightly lower",
  "diff_percentage": 6.8,
  "confidence": 0.89,
  "baseline": "vision_baseline.png",
  "current": "vision_modified.png"
}
```

**Command**:
```bash
pytest -v tests/test_cargain_login.py::test_vision_validation_login_button
```

---

### Test Case #4: Incorrect Credentials Handling

**Purpose**: Validate vision-based error detection

**Steps**:
1. Navigate to login page
2. Capture before-error screenshot
3. Enter invalid credentials: `invalid_user_12345` / `invalid_password_12345`
4. Click login button
5. Wait for error toast to appear
6. Capture after-error screenshot
7. Run `VisionAnalyzer.detect_visual_anomalies()`
8. Verify error toast detected

**Expected Result**:  
✅ Error toast appears (red background, error message)  
✅ VisionAnalyzer detects anomaly  
✅ AI explanation: "Error message appeared on top"  
✅ Dashboard metrics updated

**Command**:
```bash
pytest -v tests/test_cargain_login.py::test_incorrect_credentials_error_handling
```

---

### Test Case #5: Docker Regression Check

**Purpose**: End-to-end validation in Docker environment

**Steps**:
1. Start Docker services: `docker-compose up -d api dashboard`
2. Run test suite via Docker
3. Verify logs updated (`healing_log.json`, `vision_cache.json`)
4. Check Dashboard shows healing entries
5. Verify resource usage < 500MB

**Expected Result**:  
✅ All tests pass in Docker environment  
✅ Logs synchronized across containers  
✅ Dashboard accessible at http://localhost:8501  
✅ Memory usage < 500MB total

**Command**:
```bash
docker-compose run --rm tests pytest -v tests/test_cargain_login.py::test_docker_regression_check
```

---

## 🛠️ Setup Instructions

### 1. Add Test Credentials to .env

Copy `.env.example` to `.env` and add your CarGain credentials:

```bash
# Copy example file
cp .env.example .env

# Edit .env and add:
CARGAIN_USERNAME=your_actual_username
CARGAIN_PASSWORD=your_actual_password
```

### 2. Ensure AI Provider is Configured

Verify your AI provider API key is set in `.env`:

```bash
# Example: Using Groq (free and fast)
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# For vision testing, use Gemini or OpenAI
VISION_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Playwright Browsers (if not in Docker)

```bash
# Local testing only (not needed in Docker)
playwright install chromium
```

### 4. Create Screenshots Directory

```bash
mkdir -p reports/screenshots/cargain
```

---

## 🚀 Running Tests

### Local Testing (Host Machine)

**Run all CarGain tests**:
```bash
pytest -v tests/test_cargain_login.py
```

**Run specific test**:
```bash
pytest -v tests/test_cargain_login.py::test_broken_locator_ai_healing
```

**Run with detailed output**:
```bash
pytest -v -s tests/test_cargain_login.py
```

**Run with HTML report**:
```bash
pytest -v tests/test_cargain_login.py --html=reports/cargain_test_report.html
```

---

### Docker Testing (Containerized)

**1. Build test container** (if not already built):
```bash
docker-compose build tests
```

**2. Start API and Dashboard services**:
```bash
docker-compose up -d api dashboard
```

**3. Run tests in Docker**:
```bash
docker-compose run --rm tests pytest -v tests/test_cargain_login.py
```

**4. View logs**:
```bash
# Healing logs
cat logs/healing_log.json

# Vision cache
cat logs/vision_cache.json
```

**5. Open Dashboard**:
```
http://localhost:8501
```

Navigate to:
- **Healing Logs** tab → See AI-Healer entries
- **History** tab → See vision cache entries
- **Metrics** tab → See performance metrics

**6. Stop containers**:
```bash
docker-compose down
```

---

## 📊 Expected Results

### Test Execution Summary

| Test Case | Expected Duration | Pass Criteria |
|-----------|------------------|---------------|
| #1 Baseline Login | 5-10s | ✅ Page loads, fields found, screenshot captured |
| #2 AI-Healer Repair | 10-15s | ✅ Broken locator healed, healing logged |
| #3 Vision Validation | 15-20s | ✅ Visual diff detected, AI explanation provided |
| #4 Error Handling | 10-15s | ✅ Error toast detected as anomaly |
| #5 Docker Regression | 20-30s | ✅ All tests pass in Docker, logs synced |

### Healing Log Structure

Expected entries in `logs/healing_log.json`:

```json
{
  "timestamp": "2025-11-12T14:30:22.123Z",
  "engine": "playwright",
  "old_locator": "#username-field-broken-id-12345",
  "new_locator": "input[formcontrolname='username']",
  "healing_source": "ai",
  "latency_ms": 342.5,
  "confidence": 0.94,
  "context_hint": "Username input field on login page",
  "page_url": "https://cargainqa.rategain.com/#/Login"
}
```

### Vision Cache Structure

Expected entries in `logs/vision_cache.json`:

```json
{
  "cache_key": "vision_baseline.png_vs_vision_modified.png",
  "similarity": 93.2,
  "diff_percentage": 6.8,
  "description": "Login button appears slightly larger, page content shifted down by ~20px",
  "confidence": 0.89,
  "baseline_path": "reports/screenshots/cargain/vision_baseline.png",
  "current_path": "reports/screenshots/cargain/vision_modified.png",
  "diff_path": "reports/screenshots/cargain/vision_diff.png",
  "timestamp": "2025-11-12T14:32:15.456Z"
}
```

### Dashboard Validation

Open http://localhost:8501 and verify:

1. **Home** tab shows:
   - Total healings count
   - AI vs Cache vs Fallback breakdown
   - Recent healing entries

2. **Healing Logs** tab shows:
   - CarGain login healing entries
   - Healing source, latency, confidence

3. **History** tab shows:
   - Vision cache entries
   - Screenshot comparisons

4. **Metrics** tab shows:
   - Performance trends
   - Healing success rate

---

## 🐛 Troubleshooting

### Issue 1: Login Page Not Loading

**Symptoms**: Page timeout, blank screen

**Solutions**:
```bash
# 1. Check internet connection
ping cargainqa.rategain.com

# 2. Try loading in browser manually
# Navigate to: https://cargainqa.rategain.com/#/Login

# 3. Increase timeout in test
# Edit test_cargain_login.py:
page.goto(CARGAIN_URL, wait_until="networkidle", timeout=60000)
```

---

### Issue 2: Locators Not Found

**Symptoms**: `Locator not found` errors

**Solutions**:
```bash
# 1. Inspect page with browser DevTools
# Right-click → Inspect → Check actual locator structure

# 2. Update locators in test file
# Edit test_cargain_login.py locator arrays

# 3. Enable AI-Healer for all locators
# Set enable_healing=True in SmartLocator initialization
```

---

### Issue 3: AI-Healer Not Working

**Symptoms**: `Healing failed after 3 attempts`

**Solutions**:
```bash
# 1. Check API key is set
cat .env | grep GROQ_API_KEY

# 2. Verify AI provider is accessible
python -c "from services.locator_repair.ai_gateway import AIGateway; print(AIGateway().test_connection())"

# 3. Check healing logs for errors
tail -f logs/healing_log.json

# 4. Try different AI provider
# Edit .env:
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
```

---

### Issue 4: Vision Analysis Fails

**Symptoms**: `Vision analysis not fully configured` skip message

**Solutions**:
```bash
# 1. Ensure VISION_PROVIDER is set
cat .env | grep VISION_PROVIDER

# 2. Verify vision provider API key
cat .env | grep GEMINI_API_KEY

# 3. Test vision provider manually
python -c "from core.vision_analyzer import VisionAnalyzer; va = VisionAnalyzer(); print(va.test_vision_api())"

# 4. Check for missing PIL/numpy dependencies
pip install pillow numpy
```

---

### Issue 5: Docker Tests Fail

**Symptoms**: Tests pass locally but fail in Docker

**Solutions**:
```bash
# 1. Rebuild Docker image with no cache
docker-compose build --no-cache tests

# 2. Check .env is mounted correctly
docker-compose run --rm tests cat .env

# 3. Verify Playwright browsers installed
docker-compose run --rm tests playwright --version

# 4. Check logs directory permissions
ls -la logs/

# 5. Run with verbose output
docker-compose run --rm tests pytest -v -s tests/test_cargain_login.py
```

---

### Issue 6: Invalid Credentials

**Symptoms**: Test #1 fails with "Invalid credentials" error

**Solutions**:
```bash
# 1. Verify credentials in .env
cat .env | grep CARGAIN

# 2. Test credentials manually in browser
# Navigate to: https://cargainqa.rategain.com/#/Login
# Try logging in with same credentials

# 3. If no valid credentials available:
# Skip Test Case #1, focus on Test Cases #2-5 (healing & vision)
pytest -v tests/test_cargain_login.py -k "not baseline"
```

---

## 📈 Success Criteria

Phase 7 is considered **complete** when:

✅ **Test Case #1**: Baseline test passes (or skips if no credentials)  
✅ **Test Case #2**: AI-Healer successfully repairs broken locator  
✅ **Test Case #3**: VisionAnalyzer detects visual changes  
✅ **Test Case #4**: Error toast detected as visual anomaly  
✅ **Test Case #5**: All tests pass in Docker environment  
✅ **Logs**: `healing_log.json` contains AI healing entries  
✅ **Dashboard**: Shows healing logs and vision cache entries  
✅ **Documentation**: This guide completed and validated  

---

## 🎯 Next Steps After Phase 7

Once Phase 7 is complete, consider:

1. **CI/CD Integration** - GitHub Actions for automated testing
2. **More Test Sites** - Expand to other real-world applications
3. **Performance Optimization** - Reduce healing latency
4. **Advanced Vision** - Object detection, layout validation
5. **PyPI Package** - Publish framework as installable package

---

## 📝 Summary

Phase 7 validates the **AI-powered test automation framework** against a **real-world production-like application**, demonstrating:

- ✅ **AI-Healer** auto-repairs broken locators
- ✅ **VisionAnalyzer** detects visual changes
- ✅ **SmartLocator** provides context-aware element location
- ✅ **Docker** containerized testing works end-to-end
- ✅ **Dashboard** visualizes healing metrics and vision cache

**This is the proof that our framework works in real-world scenarios!** 🚀

---

**End of Phase 7 Guide**

*Last Updated: November 12, 2025*  
*Version: 1.0.0*  
*Author: Ram*
