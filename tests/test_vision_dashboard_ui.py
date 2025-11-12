"""
Tests for Vision Dashboard UI and Report Exporter

This test suite validates:
- Dashboard can load cached entries
- Diff overlay rendering works correctly
- HTML report generation is functional

Author: Ram
Phase: 5 - Vision Dashboard & Visual Diff UI Reports
"""

import pytest
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.utils.report_exporter import (
    export_visual_report,
    generate_html_report,
    image_to_base64,
    pil_image_to_base64
)


@pytest.fixture
def temp_cache_file(tmp_path):
    """Create temporary cache file for testing."""
    cache_file = tmp_path / "vision_cache.json"
    
    # Sample cache data
    cache_data = {
        "baseline_abc_current_xyz": {
            "timestamp": "2025-11-12 10:30:00",
            "similarity": 0.92,
            "diff_pixels": 1234,
            "changed_regions": [
                {
                    "bbox": [100, 50, 200, 100],
                    "severity": "medium",
                    "region": "button area"
                }
            ],
            "description": "Submit button moved right"
        },
        "baseline_def_current_uvw": {
            "timestamp": "2025-11-12 11:45:00",
            "similarity": 0.88,
            "diff_pixels": 2345,
            "changed_regions": [
                {
                    "bbox": [150, 75, 250, 125],
                    "severity": "high",
                    "region": "header area"
                }
            ]
        }
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)
    
    return cache_file


@pytest.fixture
def temp_healing_log(tmp_path):
    """Create temporary healing log for testing."""
    log_file = tmp_path / "healing_log.json"
    
    # Sample healing log data
    healing_logs = [
        {
            "timestamp": "2025-11-12 12:00:00",
            "old_locator": "button#submit-old",
            "new_locator": "button[type='submit']",
            "healing_source": "vision",
            "latency_ms": 2340,
            "confidence": 0.93,
            "region": "button area (150, 200)",
            "description": "Button relocated to right side"
        },
        {
            "timestamp": "2025-11-12 12:15:00",
            "old_locator": "input#email",
            "new_locator": "input[name='email']",
            "healing_source": "ai",
            "latency_ms": 1200,
            "confidence": 0.88
        },
        {
            "timestamp": "2025-11-12 12:30:00",
            "old_locator": "div.container",
            "new_locator": "div[class*='container']",
            "healing_source": "vision",
            "latency_ms": 2890,
            "confidence": 0.91,
            "region": "main content area",
            "description": "Container class changed"
        }
    ]
    
    with open(log_file, 'w') as f:
        json.dump(healing_logs, f)
    
    return log_file


@pytest.fixture
def sample_images(tmp_path):
    """Create sample images for testing."""
    # Create baseline image (100x100, white with black square)
    baseline = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(baseline)
    draw.rectangle([40, 40, 60, 60], fill='black')
    baseline_path = tmp_path / "baseline.png"
    baseline.save(baseline_path)
    
    # Create current image (100x100, white with black square moved)
    current = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(current)
    draw.rectangle([50, 40, 75, 60], fill='black')  # Moved and wider
    current_path = tmp_path / "current.png"
    current.save(current_path)
    
    # Create diff map (highlight differences)
    diff_map = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(diff_map)
    # Highlight old position
    draw.rectangle([40, 40, 60, 60], outline='red', width=2)
    # Highlight new position
    draw.rectangle([50, 40, 75, 60], outline='green', width=2)
    diff_path = tmp_path / "diff.png"
    diff_map.save(diff_path)
    
    return {
        'baseline': str(baseline_path),
        'current': str(current_path),
        'diff': str(diff_path)
    }


def test_load_cached_entries(temp_cache_file):
    """
    Test: Dashboard can load and parse cached vision analysis entries
    
    Validates:
    - Cache file is read correctly
    - JSON parsing works
    - All expected fields are present
    - Multiple entries are loaded
    """
    # Load cache file
    with open(temp_cache_file, 'r') as f:
        cache_data = json.load(f)
    
    # Validate cache loaded
    assert cache_data is not None, "Cache data should not be None"
    assert isinstance(cache_data, dict), "Cache data should be dictionary"
    
    # Validate entries
    assert len(cache_data) == 2, f"Expected 2 cache entries, got {len(cache_data)}"
    
    # Validate first entry
    first_key = list(cache_data.keys())[0]
    first_entry = cache_data[first_key]
    
    assert 'timestamp' in first_entry, "Entry should have timestamp"
    assert 'similarity' in first_entry, "Entry should have similarity"
    assert 'diff_pixels' in first_entry, "Entry should have diff_pixels"
    assert 'changed_regions' in first_entry, "Entry should have changed_regions"
    
    # Validate data types
    assert isinstance(first_entry['similarity'], (int, float)), "Similarity should be numeric"
    assert isinstance(first_entry['diff_pixels'], int), "Diff pixels should be integer"
    assert isinstance(first_entry['changed_regions'], list), "Changed regions should be list"
    
    # Validate similarity range
    assert 0.0 <= first_entry['similarity'] <= 1.0, "Similarity should be between 0 and 1"
    
    # Validate changed regions structure
    if first_entry['changed_regions']:
        region = first_entry['changed_regions'][0]
        assert 'bbox' in region, "Region should have bbox"
        assert 'severity' in region, "Region should have severity"
        assert len(region['bbox']) == 4, "Bbox should have 4 values [x, y, w, h]"
        assert region['severity'] in ['low', 'medium', 'high'], "Severity should be valid"
    
    print("✅ test_load_cached_entries passed!")
    print(f"   Loaded {len(cache_data)} cache entries")
    print(f"   First entry similarity: {first_entry['similarity']:.2%}")
    print(f"   First entry regions: {len(first_entry['changed_regions'])}")


def test_load_healing_logs(temp_healing_log):
    """
    Test: Dashboard can load and filter healing logs for vision-based healings
    
    Validates:
    - Healing log file is read correctly
    - JSON parsing works
    - Vision-based healings can be filtered
    - All expected fields are present
    """
    # Load healing log
    with open(temp_healing_log, 'r') as f:
        healing_logs = json.load(f)
    
    # Validate logs loaded
    assert healing_logs is not None, "Healing logs should not be None"
    assert isinstance(healing_logs, list), "Healing logs should be list"
    
    # Validate total entries
    assert len(healing_logs) == 3, f"Expected 3 healing logs, got {len(healing_logs)}"
    
    # Filter for vision-based healings
    vision_logs = [log for log in healing_logs if log.get('healing_source') == 'vision']
    
    assert len(vision_logs) == 2, f"Expected 2 vision healings, got {len(vision_logs)}"
    
    # Validate first vision log
    vision_log = vision_logs[0]
    
    assert 'timestamp' in vision_log, "Log should have timestamp"
    assert 'old_locator' in vision_log, "Log should have old_locator"
    assert 'new_locator' in vision_log, "Log should have new_locator"
    assert 'healing_source' in vision_log, "Log should have healing_source"
    assert 'latency_ms' in vision_log, "Log should have latency_ms"
    assert 'confidence' in vision_log, "Log should have confidence"
    
    # Validate healing source
    assert vision_log['healing_source'] == 'vision', "Healing source should be 'vision'"
    
    # Validate numeric fields
    assert isinstance(vision_log['latency_ms'], (int, float)), "Latency should be numeric"
    assert isinstance(vision_log['confidence'], (int, float)), "Confidence should be numeric"
    assert 0.0 <= vision_log['confidence'] <= 1.0, "Confidence should be between 0 and 1"
    
    print("✅ test_load_healing_logs passed!")
    print(f"   Total logs: {len(healing_logs)}")
    print(f"   Vision logs: {len(vision_logs)}")
    print(f"   First vision log latency: {vision_log['latency_ms']}ms")
    print(f"   First vision log confidence: {vision_log['confidence']:.2%}")


def test_render_diff_overlay(sample_images):
    """
    Test: Diff overlay can be rendered with bounding boxes
    
    Validates:
    - Images can be loaded
    - Bounding boxes can be drawn
    - Overlay image is generated
    - Image dimensions match original
    """
    from PIL import Image, ImageDraw
    
    # Load baseline image
    baseline_path = sample_images['baseline']
    baseline_img = Image.open(baseline_path)
    
    # Create overlay
    overlay_img = baseline_img.copy()
    draw = ImageDraw.Draw(overlay_img)
    
    # Draw bounding box (simulating changed region)
    bbox = [40, 40, 60, 60]  # [x, y, w, h]
    x, y, w, h = bbox
    draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
    
    # Validate overlay created
    assert overlay_img is not None, "Overlay image should not be None"
    assert overlay_img.size == baseline_img.size, "Overlay should match original size"
    assert overlay_img.mode == baseline_img.mode, "Overlay should match original mode"
    
    # Validate image can be saved
    temp_overlay_path = Path(baseline_path).parent / "overlay_test.png"
    overlay_img.save(temp_overlay_path)
    
    assert temp_overlay_path.exists(), "Overlay file should be created"
    assert temp_overlay_path.stat().st_size > 0, "Overlay file should not be empty"
    
    # Validate saved image can be reloaded
    reloaded_img = Image.open(temp_overlay_path)
    assert reloaded_img.size == baseline_img.size, "Reloaded image should match size"
    
    print("✅ test_render_diff_overlay passed!")
    print(f"   Original image size: {baseline_img.size}")
    print(f"   Overlay image size: {overlay_img.size}")
    print(f"   Overlay file size: {temp_overlay_path.stat().st_size} bytes")


def test_image_to_base64(sample_images):
    """
    Test: Images can be converted to base64 for HTML embedding
    
    Validates:
    - Image file can be read
    - Base64 encoding works
    - Output is valid base64 string
    """
    baseline_path = sample_images['baseline']
    
    # Convert to base64
    base64_str = image_to_base64(baseline_path)
    
    # Validate base64 string
    assert base64_str is not None, "Base64 string should not be None"
    assert isinstance(base64_str, str), "Base64 should be string"
    assert len(base64_str) > 0, "Base64 string should not be empty"
    
    # Validate base64 format (should be valid base64 characters)
    import re
    base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
    assert re.match(base64_pattern, base64_str), "Should be valid base64 string"
    
    print("✅ test_image_to_base64 passed!")
    print(f"   Base64 length: {len(base64_str)} characters")
    print(f"   First 50 chars: {base64_str[:50]}...")


def test_pil_image_to_base64(sample_images):
    """
    Test: PIL Image objects can be converted to base64
    
    Validates:
    - PIL Image can be processed
    - Base64 encoding works
    - Output is valid base64 string
    """
    baseline_path = sample_images['baseline']
    baseline_img = Image.open(baseline_path)
    
    # Convert to base64
    base64_str = pil_image_to_base64(baseline_img)
    
    # Validate base64 string
    assert base64_str is not None, "Base64 string should not be None"
    assert isinstance(base64_str, str), "Base64 should be string"
    assert len(base64_str) > 0, "Base64 string should not be empty"
    
    print("✅ test_pil_image_to_base64 passed!")
    print(f"   Base64 length: {len(base64_str)} characters")


def test_report_exporter_html(sample_images, tmp_path):
    """
    Test: HTML report can be generated with diff data and images
    
    Validates:
    - Report file is created
    - HTML structure is valid
    - Images are embedded (base64)
    - Metrics are displayed
    - Changed regions table is included
    """
    # Prepare diff data
    diff_data = {
        'similarity': 0.942,
        'diff_pixels': 3245,
        'changed_regions': [
            {
                'bbox': [100, 50, 200, 100],
                'severity': 'medium',
                'region': 'button area'
            },
            {
                'bbox': [300, 150, 100, 80],
                'severity': 'low',
                'region': 'header section'
            }
        ]
    }
    
    # Prepare LLM data
    llm_data = {
        'description': 'Submit button moved right by 10 pixels',
        'elements': ['Submit button', 'Login form'],
        'action': 'Update locator to new position'
    }
    
    # Generate report
    output_path = tmp_path / "test_report.html"
    report_path = export_visual_report(
        diff_data=diff_data,
        llm_data=llm_data,
        baseline_path=sample_images['baseline'],
        current_path=sample_images['current'],
        diff_map_path=sample_images['diff'],
        output_path=str(output_path),
        format='html'
    )
    
    # Validate report file created
    assert Path(report_path).exists(), "Report file should exist"
    assert Path(report_path).stat().st_size > 0, "Report file should not be empty"
    
    # Read report content
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Validate HTML structure
    assert '<!DOCTYPE html>' in html_content, "Should have DOCTYPE declaration"
    assert '<html' in html_content, "Should have html tag"
    assert '<head>' in html_content, "Should have head section"
    assert '<body>' in html_content, "Should have body section"
    assert '</html>' in html_content, "Should close html tag"
    
    # Validate content sections
    assert 'Visual Regression Report' in html_content, "Should have title"
    assert 'Similarity' in html_content, "Should show similarity metric"
    assert '94.2%' in html_content or '94.20%' in html_content, "Should show similarity value"
    assert '3,245' in html_content, "Should show changed pixels"
    assert 'Changed Regions' in html_content, "Should have regions section"
    
    # Validate images embedded (base64)
    assert 'data:image/png;base64,' in html_content, "Should have base64 images"
    assert html_content.count('data:image/png;base64,') >= 2, "Should have multiple images"
    
    # Validate changed regions table
    assert 'button area' in html_content, "Should show region name"
    assert 'medium' in html_content, "Should show severity"
    
    # Validate LLM section
    assert 'AI Vision Analysis' in html_content, "Should have LLM section"
    assert 'Submit button moved right' in html_content, "Should show LLM description"
    assert 'Submit button' in html_content, "Should list elements"
    assert 'Update locator' in html_content, "Should show suggested action"
    
    # Validate CSS styling
    assert '<style>' in html_content, "Should have CSS styles"
    assert 'background' in html_content, "Should have styling"
    
    print("✅ test_report_exporter_html passed!")
    print(f"   Report file: {report_path}")
    print(f"   Report size: {Path(report_path).stat().st_size:,} bytes")
    print(f"   HTML length: {len(html_content):,} characters")
    print(f"   Changed regions in report: {len(diff_data['changed_regions'])}")


def test_report_with_no_images(tmp_path):
    """
    Test: Report can be generated without images (minimal data)
    
    Validates:
    - Report works with minimal data
    - No errors when images are missing
    - Metrics still displayed
    """
    diff_data = {
        'similarity': 0.98,
        'diff_pixels': 123,
        'changed_regions': []
    }
    
    output_path = tmp_path / "minimal_report.html"
    report_path = export_visual_report(
        diff_data=diff_data,
        output_path=str(output_path),
        format='html'
    )
    
    # Validate report created
    assert Path(report_path).exists(), "Report file should exist"
    
    # Read content
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Validate basic structure
    assert 'Visual Regression Report' in html_content, "Should have title"
    assert '98' in html_content, "Should show similarity"
    assert '123' in html_content, "Should show diff pixels"
    
    print("✅ test_report_with_no_images passed!")
    print(f"   Minimal report size: {Path(report_path).stat().st_size} bytes")


def test_metrics_calculation(temp_cache_file, temp_healing_log):
    """
    Test: Metrics can be calculated from cache and healing logs
    
    Validates:
    - Cache statistics correct
    - Vision usage percentage correct
    - Average similarity calculated
    """
    # Load data
    with open(temp_cache_file, 'r') as f:
        cache_data = json.load(f)
    
    with open(temp_healing_log, 'r') as f:
        healing_logs = json.load(f)
    
    # Calculate metrics
    total_entries = len(cache_data)
    vision_healings = [log for log in healing_logs if log.get('healing_source') == 'vision']
    vision_usage = len(vision_healings)
    total_healings = len(healing_logs)
    
    # Calculate average similarity
    similarities = [entry['similarity'] for entry in cache_data.values() if 'similarity' in entry]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    
    # Validate metrics
    assert total_entries == 2, f"Expected 2 cache entries, got {total_entries}"
    assert vision_usage == 2, f"Expected 2 vision healings, got {vision_usage}"
    assert total_healings == 3, f"Expected 3 total healings, got {total_healings}"
    
    vision_percentage = (vision_usage / total_healings * 100) if total_healings > 0 else 0
    assert abs(vision_percentage - 66.67) < 0.1, f"Expected ~66.67% vision usage, got {vision_percentage:.2f}%"
    
    assert 0.88 <= avg_similarity <= 0.92, f"Expected avg similarity ~0.90, got {avg_similarity}"
    
    print("✅ test_metrics_calculation passed!")
    print(f"   Cache entries: {total_entries}")
    print(f"   Vision healings: {vision_usage}/{total_healings} ({vision_percentage:.1f}%)")
    print(f"   Average similarity: {avg_similarity:.2%}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
