# Vision Dashboard Guide

**AI-Powered Visual Regression Testing UI**

Phase 5: Vision Dashboard & Visual Diff UI Reports  
Author: Ram  
Repository: SDET-AI-Labs/ai-powered-test-automation

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Dashboard Features](#dashboard-features)
5. [Usage Workflow](#usage-workflow)
6. [Report Export](#report-export)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **Vision Dashboard** is an interactive Streamlit-based web application that provides a comprehensive UI for visual regression testing. It integrates with the Vision Analyzer (Phase 4) to offer:

- **Side-by-side image comparison** with visual diff overlays
- **AI-powered analysis** using Vision LLM (Gemini/GPT-4V)
- **Historical tracking** of all vision analyses
- **Healing log exploration** for vision-based locator repairs
- **Performance metrics** dashboard
- **Export capabilities** for HTML/PDF reports

### Key Benefits

✅ **User-Friendly**: No coding required - upload images and get insights  
✅ **AI-Powered**: Leverage Vision LLM for intelligent change detection  
✅ **Comprehensive**: View all aspects of visual testing in one place  
✅ **Shareable**: Export professional reports for stakeholders  
✅ **Fast**: Caching ensures repeated analyses are instant

---

## 🏗️ Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Vision Dashboard (UI)                       │
│                     (ui/vision_dashboard.py)                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Streamlit Interface
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│  VisionAnalyzer  │  │  Report Exporter │
│  (core/vision)   │  │  (ui/utils)      │
└──────────────────┘  └──────────────────┘
        │                    │
        │                    │
        ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│  Cache/Logs      │  │  HTML/PDF        │
│  vision_cache    │  │  Reports         │
│  healing_log     │  │  (reports/)      │
└──────────────────┘  └──────────────────┘
```

### Data Flow

```
1. User uploads images
   ↓
2. VisionAnalyzer compares images
   ↓
3. Detect visual anomalies
   ↓
4. Optional: Ask Vision LLM
   ↓
5. Display results with overlays
   ↓
6. Cache results for future use
   ↓
7. Export report (HTML/PDF)
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Install required dependencies
pip install streamlit pillow numpy
pip install pdfkit reportlab  # Optional for PDF export
```

### Launch Dashboard

```bash
# From project root
streamlit run ui/vision_dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### First Time Setup

1. **Configure Vision Provider**: Use sidebar to select provider (Gemini/OpenAI)
2. **Set API Keys**: Ensure `.env` has `GEMINI_API_KEY` or `OPENAI_API_KEY`
3. **Upload Images**: Navigate to "Compare Images" page

---

## 📊 Dashboard Features

### 1. Home Page 🏠

**Quick Overview Dashboard**

- **Real-time Metrics**
  - Cache Entries count
  - Total Healings count
  - Vision Healings count
  - Vision Usage percentage

- **Navigation Links**
  - Quick access to all sections

**Screenshot:**
```
┌─────────────────────────────────────────┐
│  👁️ Vision Dashboard                    │
│  AI-Powered Visual Regression Testing   │
├─────────────────────────────────────────┤
│  Welcome Message & Feature List         │
├─────────────────────────────────────────┤
│  📊 Metrics Bar                          │
│  [Cache: 15] [Healings: 8] [Usage: 25%] │
└─────────────────────────────────────────┘
```

---

### 2. Compare Images 📊

**Interactive Image Comparison Tool**

#### Features:

- **Dual Upload**: Upload baseline and current screenshots
- **Real-time Preview**: See images side-by-side
- **Analysis Button**: Trigger VisionAnalyzer
- **Diff Overlay**: Visual bounding boxes on changed regions
- **Metrics Display**:
  - Similarity percentage
  - Changed pixels count
  - Changed regions count
  - Anomalies detected

- **Optional LLM Analysis**: Toggle Vision LLM for AI insights

#### Workflow:

1. Upload **Baseline** image (left panel)
2. Upload **Current** image (right panel)
3. Click **"🔍 Analyze Differences"**
4. Review metrics and visual overlays
5. Optional: Enable **"Use Vision LLM Analysis"** for AI description

#### Visual Overlay Legend:

- 🔴 **Red Box** = High severity change
- 🟠 **Orange Box** = Medium severity change
- 🟡 **Yellow Box** = Low severity change

**Example Output:**
```
Similarity: 94.2% ↓ 0.8%
Changed Pixels: 3,245
Changed Regions: 2
Anomalies: 1

[Baseline]    [Current]     [Diff Map]
   📸            📸            🔍
  Image        Image       Highlighted
```

---

### 3. History 📜

**Cached Analysis Browser**

#### Features:

- **All Past Analyses**: View complete history from `vision_cache.json`
- **Sortable List**: Sorted by timestamp (newest first)
- **Expandable Entries**: Click to see details
- **Metadata Display**:
  - Cache key (truncated)
  - Timestamp
  - Similarity score
  - Diff pixels
  - Changed regions count
  - AI description (if available)

#### Use Case:

Review past visual comparisons without re-running analysis. Perfect for:
- Auditing previous test runs
- Comparing trends over time
- Debugging specific test failures

**Example Entry:**
```
Entry #3 - Similarity: 97.5%
┌──────────────────────────────────────┐
│ Cache Key: baseline_xyz_current_...  │
│ Timestamp: 2025-11-12 14:30:22      │
│ Similarity: 97.5%                    │
│ Diff Pixels: 1,024                   │
│ Changed Regions: 1                   │
│                                      │
│ AI Description:                      │
│ "Submit button moved 10px to the    │
│  right, color changed from blue to  │
│  green."                            │
└──────────────────────────────────────┘
```

---

### 4. Healing Logs 🔧

**Vision-Based Healing Explorer**

#### Features:

- **Filtered View**: Shows only `healing_source: "vision"` entries
- **Statistics**:
  - Total healing events
  - Vision-based healings count
- **Detailed Log Entries**:
  - Old locator (failed)
  - New locator (healed)
  - Healing source
  - Timestamp
  - Latency (ms)
  - Confidence score
  - Region description
  - AI description

#### Use Case:

Track when AIHealer uses visual analysis as fallback healing:
- Monitor vision fallback frequency
- Validate healing accuracy
- Debug locator repair issues

**Example Log:**
```
Healing #2 - 2025-11-12 15:45:10
┌──────────────────────────────────────┐
│ Old Locator: button#submit-old       │
│ New Locator: button[type='submit']  │
│ Source: vision                       │
│                                      │
│ Timestamp: 2025-11-12 15:45:10      │
│ Latency: 2,340ms                     │
│ Confidence: 93%                      │
│                                      │
│ Region: button area (150, 200)      │
│                                      │
│ Description:                         │
│ "Button relocated to right side"    │
└──────────────────────────────────────┘
```

---

### 5. Metrics 📈

**Performance Dashboard**

#### Metrics Displayed:

1. **Overall Statistics**
   - Cache Entries
   - Total Healings
   - Vision Healings
   - Vision Usage %

2. **Similarity Distribution**
   - Bar chart of all similarity scores
   - Average similarity
   - Minimum similarity
   - Maximum similarity

3. **Cache Statistics** (if VisionAnalyzer active)
   - Total Entries
   - Total Calls
   - Cache Hits
   - Hit Rate %

#### Use Case:

- Monitor system performance
- Identify trends (e.g., decreasing similarity = UI instability)
- Optimize cache usage
- Plan Vision LLM API quota

**Example Metrics:**
```
┌─────────────────────────────────────┐
│ Overall Statistics                   │
│ [Cache: 20] [Healings: 12]          │
│ [Vision: 3] [Usage: 25%]            │
├─────────────────────────────────────┤
│ Similarity Distribution              │
│ █████████ 95%                       │
│ ██████ 90%                          │
│ ████ 85%                            │
├─────────────────────────────────────┤
│ Cache Statistics                     │
│ Hit Rate: 87%                       │
│ Total Calls: 23                     │
│ Cache Hits: 20                      │
└─────────────────────────────────────┘
```

---

## 🔄 Usage Workflow

### For QA Teams

#### Daily Visual Testing Workflow:

```
1. Capture Baseline Screenshots
   ↓
2. Run Tests (automated or manual)
   ↓
3. Capture Current Screenshots
   ↓
4. Upload to Vision Dashboard
   ↓
5. Analyze Differences
   ↓
6. Review Anomalies
   ↓
7. Export Report for Stakeholders
   ↓
8. Fix Issues if needed
   ↓
9. Update Baselines
```

### For Developers

#### Debugging Visual Failures:

```
1. Test Fails with Locator Error
   ↓
2. Check Healing Logs (🔧 tab)
   ↓
3. Find Vision-Based Healing
   ↓
4. Review AI Description
   ↓
5. Identify Root Cause (UI change)
   ↓
6. Fix Locator or Update UI
```

### For Managers

#### Weekly Reporting:

```
1. Open Metrics Dashboard (📈 tab)
   ↓
2. Review Vision Usage Trends
   ↓
3. Check Similarity Averages
   ↓
4. Export Historical Reports
   ↓
5. Share with Team
```

---

## 📄 Report Export

### HTML Report Generation

#### From Dashboard:

Currently manual via code integration. Future versions will have UI button.

#### Programmatic Export:

```python
from ui.utils.report_exporter import export_visual_report

# After analysis
diff_data = {
    'similarity': 0.942,
    'diff_pixels': 3245,
    'changed_regions': [
        {'bbox': [100, 50, 200, 100], 'severity': 'medium'}
    ]
}

llm_data = {
    'description': 'Submit button moved right',
    'elements': ['Submit button'],
    'action': 'Update locator to new position'
}

report_path = export_visual_report(
    diff_data=diff_data,
    llm_data=llm_data,
    baseline_path='baseline.png',
    current_path='current.png',
    diff_map_path='diff.png',
    output_path='reports/vision_report.html',
    format='html'
)

print(f"Report saved: {report_path}")
```

### Report Features

**HTML Report Includes:**

1. **Header**
   - Title: "Visual Regression Report"
   - Timestamp

2. **Metrics Section**
   - Similarity (with color coding)
   - Changed Pixels
   - Changed Regions
   - Status (✓ or ⚠)

3. **Images Section**
   - Baseline (embedded base64)
   - Current (embedded base64)
   - Diff Map (embedded base64)

4. **Changed Regions Table**
   - Region name
   - Position (x, y)
   - Size (width × height)
   - Severity badge

5. **AI Analysis Section** (if available)
   - Description
   - Changed Elements list
   - Suggested Action

6. **Footer**
   - Generation info
   - Copyright

### PDF Export (Optional)

Requires `pdfkit` and `wkhtmltopdf`:

```bash
# Install dependencies
pip install pdfkit

# Install wkhtmltopdf
# Windows: https://wkhtmltopdf.org/downloads.html
# Mac: brew install wkhtmltopdf
# Linux: sudo apt-get install wkhtmltopdf
```

```python
# Export as PDF
report_path = export_visual_report(
    diff_data=diff_data,
    output_path='reports/vision_report.pdf',
    format='pdf'  # Will generate HTML first, then convert
)
```

---

## ⚡ Performance Considerations

### Caching Strategy

**Vision Cache (`logs/vision_cache.json`)**

- **What's Cached**: Image comparison results, LLM analysis
- **Cache Key**: Hash of (baseline + current + provider)
- **Hit Rate**: Typically 60-80% in repeated test runs
- **Benefits**: 
  - 90% faster on cache hits
  - Reduced API costs
  - Consistent results

**When Cache is Used:**

- ✅ Same images compared again
- ✅ Same provider settings
- ✅ Cache not manually cleared

**When Cache Misses:**

- ❌ Images changed (even 1 pixel)
- ❌ Provider changed (Gemini → OpenAI)
- ❌ Cache file deleted

### API Rate Limits

**Gemini Vision:**
- Free tier: 60 requests/minute
- Performance: ~2-3s per request

**GPT-4 Vision:**
- Paid tier: varies by plan
- Performance: ~3-4s per request

**Best Practices:**

1. **Use Cache Aggressively**: Don't clear unless needed
2. **Batch Analysis**: Analyze multiple images in one session
3. **Schedule Off-Peak**: Run during low-traffic hours
4. **Monitor Quotas**: Track API usage in provider dashboard

### Image Size Optimization

**Recommendations:**

- **Max Resolution**: 1920×1080 (Full HD)
- **File Format**: PNG for precision, JPEG for size
- **Compression**: Use moderate compression (80-90% quality)
- **File Size**: Aim for <2MB per image

**Why:**

- Faster upload
- Faster analysis
- Lower bandwidth costs
- API payload limits

### Dashboard Performance

**Streamlit Optimization:**

- **Session State**: Reuses VisionAnalyzer instance
- **Lazy Loading**: Images loaded on-demand
- **Caching**: Streamlit's `@st.cache_data` for expensive ops
- **Pagination**: Future: paginate history for large datasets

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Dashboard Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit pillow numpy
```

#### 2. Images Not Displaying

**Error:** Images show as blank or corrupted

**Solution:**
- Ensure images are valid PNG/JPEG
- Check file permissions
- Verify paths are correct
- Try re-uploading

#### 3. Vision LLM Fails

**Error:** "API key not found" or "Rate limit exceeded"

**Solution:**
- Check `.env` has `GEMINI_API_KEY` or `OPENAI_API_KEY`
- Verify API key is valid (test in provider console)
- Check rate limits in provider dashboard
- Wait and retry

#### 4. Cache Not Working

**Error:** Every analysis triggers API call

**Solution:**
- Check `logs/vision_cache.json` exists and is writable
- Verify images are identical (hash match)
- Ensure provider setting unchanged
- Clear and rebuild cache

#### 5. PDF Export Fails

**Error:** "pdfkit not installed" or "wkhtmltopdf not found"

**Solution:**
```bash
# Install Python package
pip install pdfkit

# Install wkhtmltopdf
# Windows: Download from https://wkhtmltopdf.org/downloads.html
# Mac: brew install wkhtmltopdf
# Linux: sudo apt-get install wkhtmltopdf

# Add to PATH if needed
```

#### 6. Diff Overlay Not Showing

**Error:** No bounding boxes on images

**Solution:**
- Increase anomaly detection threshold (lower = more sensitive)
- Ensure images are actually different
- Check `changed_regions` in diff data
- Verify PIL/ImageDraw installed

### Debug Mode

Enable Streamlit debug mode:

```bash
streamlit run ui/vision_dashboard.py --logger.level=debug
```

Check logs in terminal for detailed error messages.

---

## 📞 Support

### Get Help

- **GitHub Issues**: [SDET-AI-Labs/ai-powered-test-automation/issues](https://github.com/SDET-AI-Labs/ai-powered-test-automation/issues)
- **Documentation**: `/docs/` folder in repository
- **Contact**: ram@example.com (replace with actual contact)

### Contribute

Contributions welcome! See `CONTRIBUTING.md` for guidelines.

---

## 📜 License

Copyright © 2025 SDET-AI-Labs  
Licensed under MIT License

---

**End of Vision Dashboard Guide**

*Last Updated: November 12, 2025*  
*Version: 1.0.0*  
*Author: Ram*
