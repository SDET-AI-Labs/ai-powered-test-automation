# Vision Testing Module
## AI-Powered Visual Validation for Test Automation

**Author:** Ram  
**Date:** November 12, 2025  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [VisionAnalyzer API](#visionanalyzer-api)
4. [Integration with AIHealer](#integration-with-aihealer)
5. [Sample LLM Prompts](#sample-llm-prompts)
6. [Example Outputs](#example-outputs)
7. [Performance Considerations](#performance-considerations)
8. [Usage Examples](#usage-examples)
9. [Testing](#testing)

---

## 🎯 Overview

The **Vision Testing Module** extends the AI-powered test automation framework with **visual validation** capabilities. It detects UI changes that pure DOM-based healing might miss, using multimodal LLMs (Gemini Vision, GPT-4 Vision) to analyze screenshots and suggest locator fixes.

### Key Features

✅ **Visual Diff Detection** - Pixel-by-pixel comparison using PIL + NumPy  
✅ **AI Vision Analysis** - Multimodal LLM describes visual changes  
✅ **Visual Fallback Healing** - Suggests locators based on visual context  
✅ **Result Caching** - Cached analysis for performance  
✅ **Multi-Provider Support** - Gemini Vision, GPT-4V, OpenRouter Vision  

### Use Cases

- **Detect visual regressions** - Button moved, color changed, size changed
- **Visual healing fallback** - When DOM locators and heuristics fail
- **Screenshot comparison** - Baseline vs current UI validation
- **Cross-browser visual testing** - Detect rendering differences

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Execution                           │
│                                                              │
│  Playwright/Selenium Test  →  Locator Fails  →  AIHealer   │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │         AIHealer                  │
        │                                   │
        │  1. Check Cache      ────────┐   │
        │  2. Try AI Healing           │   │
        │  3. Try Heuristic Fallback   │   │
        │  4. Try Visual Fallback ◄────┘   │
        └───────────┬───────────────────────┘
                    │
                    ▼
        ┌───────────────────────────────────┐
        │      VisionAnalyzer               │
        │                                   │
        │  • compare_images()               │
        │  • detect_visual_anomalies()      │
        │  • analyze_with_llm()             │
        │  • suggest_locator_from_visuals() │
        └───────────┬───────────────────────┘
                    │
                    ├─► Local Image Processing (PIL + NumPy)
                    │
                    └─► Vision LLM (Gemini/GPT-4V via AIGateway)
```

### Component Flow

1. **Test Fails** → Locator not found
2. **AIHealer** → Tries cache, AI, heuristic fallback
3. **Visual Fallback** → If all fail, capture screenshots
4. **VisionAnalyzer** → Compare baseline vs current
5. **Visual Diff** → Detect anomalies (position, size, style changes)
6. **LLM Analysis** → Vision LLM describes changes
7. **Locator Suggestion** → Suggest new locator based on visual context
8. **Healing Complete** → Log with `healing_source: "vision"`

---

## 🔧 VisionAnalyzer API

### Class: `VisionAnalyzer`

```python
from core.vision_analyzer import VisionAnalyzer

analyzer = VisionAnalyzer(
    provider="gemini",           # Vision LLM provider
    cache_dir="logs/vision_cache",  # Cache directory
    ai_gateway=None              # Optional AIGateway instance
)
```

---

### Method: `compare_images()`

**Signature:**
```python
def compare_images(
    baseline_path: str,
    current_path: str,
    save_diff: bool = True
) -> Dict[str, Any]
```

**Description:**  
Performs pixel-by-pixel comparison between two images.

**Parameters:**
- `baseline_path` (str): Path to baseline/expected image
- `current_path` (str): Path to current/actual image
- `save_diff` (bool): Save diff map image to cache

**Returns:**
```python
{
    "similarity": 0.95,           # 0.0-1.0 score
    "diff_pixels": 1234,          # Number of changed pixels
    "diff_percentage": 5.2,       # Percentage of pixels changed
    "regions": [                  # Changed regions
        {
            "x": 100,
            "y": 50,
            "width": 200,
            "height": 80,
            "area": "full_diff"
        }
    ],
    "diff_map_path": "logs/vision_cache/diff_20251112_143022.png",
    "baseline_size": (1920, 1080),
    "current_size": (1920, 1080),
    "timestamp": "2025-11-12T14:30:22.123456"
}
```

**Example:**
```python
diff = analyzer.compare_images("baseline.png", "current.png")
if diff["similarity"] < 0.95:
    print(f"Visual change detected: {diff['diff_percentage']}%")
```

---

### Method: `detect_visual_anomalies()`

**Signature:**
```python
def detect_visual_anomalies(
    baseline_path: str,
    current_path: str,
    threshold: float = 0.8
) -> List[Dict[str, Any]]
```

**Description:**  
Detects significant visual changes above similarity threshold.

**Parameters:**
- `baseline_path` (str): Path to baseline image
- `current_path` (str): Path to current image
- `threshold` (float): Similarity threshold (0.0-1.0). Below this = anomaly.

**Returns:**
```python
[
    {
        "region": {"x": 100, "y": 50, "width": 200, "height": 80},
        "severity": "high",  # low | medium | high | critical
        "description": "Visual difference detected: 15.3% pixels changed",
        "confidence": 0.85,
        "diff_map_path": "logs/vision_cache/diff_20251112_143022.png",
        "timestamp": "2025-11-12T14:30:22.123456"
    }
]
```

**Example:**
```python
anomalies = analyzer.detect_visual_anomalies("baseline.png", "current.png", 0.9)
if anomalies:
    print(f"Found {len(anomalies)} visual anomalies")
    for anomaly in anomalies:
        print(f"  - {anomaly['severity']}: {anomaly['description']}")
```

---

### Method: `analyze_with_llm()`

**Signature:**
```python
def analyze_with_llm(
    image_path: str,
    prompt: str = "",
    use_cache: bool = True
) -> Dict[str, Any]
```

**Description:**  
Asks Vision LLM to analyze an image and describe differences.

**Parameters:**
- `image_path` (str): Path to image (diff map or screenshot)
- `prompt` (str): Question/prompt for LLM
- `use_cache` (bool): Use cached results if available

**Returns:**
```python
{
    "description": "The submit button has moved 20px to the left...",
    "elements_affected": ["submit_button", "cancel_button"],
    "suggested_action": "update_locator",
    "confidence": 0.93,
    "timestamp": "2025-11-12T14:30:22.123456",
    "prompt": "What UI elements changed in this screenshot?",
    "image_path": "logs/vision_cache/diff_20251112_143022.png"
}
```

**Example:**
```python
result = analyzer.analyze_with_llm(
    "diff_map.png",
    "What UI elements changed in this screenshot?"
)
print(result["description"])
```

---

### Method: `suggest_locator_from_visuals()`

**Signature:**
```python
def suggest_locator_from_visuals(
    visual_diffs: List[Dict[str, Any]],
    context_hint: str = "",
    engine: str = "Playwright"
) -> Optional[str]
```

**Description:**  
Suggests a new locator based on visual differences.

**Parameters:**
- `visual_diffs` (list): List of anomalies from `detect_visual_anomalies()`
- `context_hint` (str): Original context hint (e.g., "Submit button")
- `engine` (str): Framework engine (Playwright, Selenium)

**Returns:**
```python
"role=button[name='Submit']"  # Playwright locator
# or
"//button[contains(text(), 'Submit')]"  # XPath locator
# or
None  # If unable to suggest
```

**Example:**
```python
anomalies = analyzer.detect_visual_anomalies("baseline.png", "current.png")
if anomalies:
    locator = analyzer.suggest_locator_from_visuals(
        anomalies,
        context_hint="Submit",
        engine="Playwright"
    )
    if locator:
        print(f"Suggested locator: {locator}")
```

---

## 🔗 Integration with AIHealer

### Enabling Visual Fallback

```python
from core.ai_healer import AIHealer

healer = AIHealer(
    log_path="logs/healing_log.json",
    cache_path="logs/healing_cache.json",
    enable_vision=True,                    # Enable visual fallback
    baseline_screenshot="baseline.png",    # Baseline image
    current_screenshot="current.png"       # Current image
)

# Attempt healing (will use vision fallback if AI/heuristic fail)
new_locator = healer.heal_locator(
    page,
    failed_locator="#old-button",
    context_hint="Submit button",
    engine="Playwright"
)
```

### Healing Flow with Vision

```
1. Cache Check      → Hit? Return cached locator
                     ↓ Miss
2. AI Healing       → Success? Return AI locator
                     ↓ Fail (returns same locator)
3. Heuristic Fallback → Success? Return heuristic locator
                     ↓ Fail
4. Visual Fallback  → Enabled? Compare screenshots
                     ↓ Visual diffs found
5. Vision Analysis  → LLM analyzes differences
                     ↓ Locator suggested
6. Return Locator   → healing_source = "vision"
```

### Log Structure with Vision

```json
{
  "timestamp": "2025-11-12T14:30:22.123456",
  "engine": "Playwright",
  "old_locator": "#old-button",
  "new_locator": "role=button[name='Submit']",
  "healing_source": "vision",
  "latency_ms": 2340.5,
  "context_hint": "Submit button",
  "success": true
}
```

---

## 💬 Sample LLM Prompts

### Prompt 1: General Visual Diff Analysis

```python
prompt = """Analyze this screenshot and describe any UI changes or visual differences.

Focus on:
- Elements that moved or changed position
- Elements that changed size or style
- Elements that appeared or disappeared
- Any other significant visual changes

Return your analysis in a structured format."""
```

**Sample Response:**
```
The submit button has moved approximately 20 pixels to the left compared to the baseline.
The button's background color has changed from blue (#0066CC) to green (#00CC66).
A new "Cancel" button has appeared below the submit button.
The form header text size has increased from 16px to 20px.
```

---

### Prompt 2: Element-Specific Analysis

```python
prompt = f"""Based on this visual diff, suggest a locator for: "{context_hint}"

The element appears to have changed position or appearance.
Framework: {engine}

Suggest a robust locator strategy (CSS, XPath, or text-based) that would work with the changed element."""
```

**Sample Response:**
```
For the "Submit" button that has moved:
- Recommended: role=button[name='Submit'] (Playwright)
- Alternative: //button[text()='Submit'] (XPath)
- Avoid: #submit-btn (ID may have changed)

The button is now located 20px left of its original position but retains its text content,
making text-based locators more reliable than position-based selectors.
```

---

### Prompt 3: Severity Assessment

```python
prompt = """Rate the severity of these visual changes:
1. Minor: Cosmetic only (color, font)
2. Moderate: Position/size changed but element still visible
3. Critical: Element missing or completely relocated

Provide your assessment and reasoning."""
```

**Sample Response:**
```
Severity: MODERATE

Reasoning:
- The submit button moved 20px but remains in the same general area
- The button is still visible and functional
- Users can still find and interact with the button
- However, automated tests relying on pixel-perfect positioning will fail

Recommendation: Update locators to use text/role-based selectors instead of position.
```

---

## 📊 Example Outputs

### Example 1: Button Moved Detection

**Input:**
- Baseline: Button at position (100, 50)
- Current: Button at position (120, 50)

**Output:**
```json
{
  "similarity": 0.92,
  "diff_percentage": 8.3,
  "regions": [
    {
      "x": 100,
      "y": 50,
      "width": 200,
      "height": 40,
      "area": "full_diff"
    }
  ],
  "llm_analysis": {
    "description": "Submit button moved 20px to the right",
    "elements_affected": ["button"],
    "suggested_action": "update_locator"
  },
  "suggested_locator": "text=Submit"
}
```

---

### Example 2: Color Change Detection

**Input:**
- Baseline: Blue button (#0066CC)
- Current: Green button (#00CC66)

**Output:**
```json
{
  "similarity": 0.85,
  "diff_percentage": 15.2,
  "regions": [
    {
      "x": 100,
      "y": 50,
      "width": 150,
      "height": 40,
      "area": "full_diff"
    }
  ],
  "llm_analysis": {
    "description": "Button background color changed from blue to green",
    "elements_affected": ["button"],
    "suggested_action": "no_action_needed"
  },
  "severity": "low"
}
```

---

### Example 3: Element Disappeared

**Input:**
- Baseline: Button visible
- Current: Button not present

**Output:**
```json
{
  "similarity": 0.65,
  "diff_percentage": 35.0,
  "regions": [
    {
      "x": 100,
      "y": 50,
      "width": 150,
      "height": 40,
      "area": "full_diff"
    }
  ],
  "llm_analysis": {
    "description": "Submit button is no longer visible in the screenshot",
    "elements_affected": ["button"],
    "suggested_action": "manual_review"
  },
  "severity": "critical",
  "suggested_locator": null
}
```

---

## ⚡ Performance Considerations

### Caching Strategy

✅ **Visual Analysis Results Cached**
- Cache key: MD5(image_path + prompt)
- Storage: `logs/vision_cache/vision_cache.json`
- Invalidation: Manual via `clear_cache()`

✅ **Diff Maps Saved**
- Location: `logs/vision_cache/diff_YYYYMMDD_HHMMSS.png`
- Auto-cleanup: Not implemented (manual cleanup required)

### API Rate Limits

| Provider | Rate Limit | Cost | Latency |
|----------|-----------|------|---------|
| **Gemini Vision** | 60 req/min (free) | FREE | ~2.3s avg |
| **GPT-4V Mini** | Varies by tier | $0.00015/image | ~1.8s avg |
| **OpenRouter** | Depends on model | Varies | ~2.5s avg |

### Optimization Tips

1. **Use Caching Aggressively**
   ```python
   analyzer.analyze_with_llm(image, prompt, use_cache=True)
   ```

2. **Increase Similarity Threshold**
   ```python
   # Only detect significant changes (fewer API calls)
   anomalies = analyzer.detect_visual_anomalies(baseline, current, threshold=0.9)
   ```

3. **Skip Vision for Minor Diffs**
   ```python
   diff = analyzer.compare_images(baseline, current)
   if diff["similarity"] >= 0.95:
       # Skip LLM analysis for minor changes
       pass
   ```

4. **Batch Analysis**
   ```python
   # Analyze multiple images in one session
   analyzer = VisionAnalyzer(cache_dir="logs/vision_cache")
   for baseline, current in image_pairs:
       analyzer.compare_images(baseline, current)  # Cached
   ```

---

## 📝 Usage Examples

### Example 1: Standalone Visual Diff

```python
from core.vision_analyzer import VisionAnalyzer

analyzer = VisionAnalyzer(provider="gemini")

# Compare images
diff = analyzer.compare_images("baseline.png", "current.png")

if diff["similarity"] < 0.95:
    print(f"⚠️ Visual change detected!")
    print(f"   Similarity: {diff['similarity']:.2%}")
    print(f"   Changed pixels: {diff['diff_pixels']:,}")
    print(f"   Diff map: {diff['diff_map_path']}")
```

**Output:**
```
⚠️ Visual change detected!
   Similarity: 92.00%
   Changed pixels: 12,345
   Diff map: logs/vision_cache/diff_20251112_143022.png
```

---

### Example 2: Visual Anomaly Detection

```python
from core.vision_analyzer import VisionAnalyzer

analyzer = VisionAnalyzer()

# Detect anomalies
anomalies = analyzer.detect_visual_anomalies(
    "baseline.png",
    "current.png",
    threshold=0.90
)

for anomaly in anomalies:
    print(f"🔴 {anomaly['severity'].upper()}: {anomaly['description']}")
    print(f"   Region: {anomaly['region']}")
    print(f"   Confidence: {anomaly['confidence']:.2%}")
```

**Output:**
```
🔴 HIGH: Visual difference detected: 15.3% pixels changed
   Region: {'x': 100, 'y': 50, 'width': 200, 'height': 80}
   Confidence: 85.00%
```

---

### Example 3: Integrated with AIHealer

```python
from core.ai_healer import AIHealer
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Capture baseline
    page.goto("https://example.com/login")
    page.screenshot(path="baseline.png")
    
    # ... UI changes ...
    
    # Capture current
    page.screenshot(path="current.png")
    
    # Create healer with vision
    healer = AIHealer(
        enable_vision=True,
        baseline_screenshot="baseline.png",
        current_screenshot="current.png"
    )
    
    # Attempt healing
    new_locator = healer.heal_locator(
        page,
        failed_locator="#old-submit-btn",
        context_hint="Submit button",
        engine="Playwright"
    )
    
    print(f"Healed locator: {new_locator}")
    
    browser.close()
```

---

## 🧪 Testing

### Run Visual Validation Tests

```bash
# Install dependencies
pip install pillow numpy

# Run all visual tests
pytest -s -v tests/test_visual_validation.py

# Run specific test
pytest -s -v tests/test_visual_validation.py::test_visual_diff_detection
```

### Expected Test Results

```
tests/test_visual_validation.py::test_visual_diff_detection PASSED
tests/test_visual_validation.py::test_visual_diff_identical_images PASSED
tests/test_visual_validation.py::test_detect_visual_anomalies_with_differences PASSED
tests/test_visual_validation.py::test_detect_visual_anomalies_no_differences PASSED
tests/test_visual_validation.py::test_llm_visual_analysis PASSED
tests/test_visual_validation.py::test_llm_visual_analysis_caching PASSED
tests/test_visual_validation.py::test_suggest_locator_from_visuals PASSED
tests/test_visual_validation.py::test_suggest_locator_no_anomalies PASSED
tests/test_visual_validation.py::test_visual_fallback_healing_integration PASSED
tests/test_visual_validation.py::test_visual_fallback_disabled PASSED
tests/test_visual_validation.py::test_vision_cache_stats PASSED
tests/test_visual_validation.py::test_vision_clear_cache PASSED

========================= 12 passed in 3.45s =========================
```

---

## 🚀 Next Steps

### Phase 5 (Future): UI Report Dashboard

Consider adding a Streamlit dashboard for visual diff reports:

```python
# streamlit run vision_dashboard.py

import streamlit as st
from core.vision_analyzer import VisionAnalyzer

st.title("Vision Testing Dashboard")

baseline = st.file_uploader("Baseline Image", type=['png', 'jpg'])
current = st.file_uploader("Current Image", type=['png', 'jpg'])

if baseline and current:
    analyzer = VisionAnalyzer()
    diff = analyzer.compare_images(baseline, current)
    
    st.metric("Similarity", f"{diff['similarity']:.2%}")
    st.metric("Changed Pixels", diff['diff_pixels'])
    
    st.image(diff['diff_map_path'], caption="Visual Diff Map")
```

---

## 📚 References

- [Gemini Vision API](https://ai.google.dev/gemini-api/docs/vision)
- [GPT-4 Vision](https://platform.openai.com/docs/guides/vision)
- [PIL (Pillow) Documentation](https://pillow.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)

---

**Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**Contributors:** Ram (AI Assistant)
