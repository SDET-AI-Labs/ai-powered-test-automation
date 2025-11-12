"""
test_visual_validation.py
-------------------------------------------------
Unit tests for Vision Testing Module:
  ✅ Visual diff detection
  ✅ LLM visual analysis
  ✅ Visual fallback healing
  ✅ Cache behavior
  ✅ Integration with AIHealer
-------------------------------------------------
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image, ImageDraw
import numpy as np
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.vision_analyzer import VisionAnalyzer
from core.ai_healer import AIHealer


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def temp_vision_analyzer(tmp_path):
    """Create VisionAnalyzer with temporary cache directory."""
    cache_dir = tmp_path / "vision_cache"
    
    # Mock AIGateway
    mock_ai = Mock()
    mock_ai.ask_vision = Mock(return_value="Button moved 20px to the left")
    
    analyzer = VisionAnalyzer(
        provider="gemini",
        cache_dir=str(cache_dir),
        ai_gateway=mock_ai
    )
    return analyzer


@pytest.fixture
def sample_images(tmp_path):
    """Create sample baseline and current images for testing."""
    # Create baseline image (100x100 white with black button)
    baseline = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(baseline)
    draw.rectangle([40, 40, 60, 60], fill='black')
    baseline_path = tmp_path / "baseline.png"
    baseline.save(baseline_path)
    
    # Create current image (button moved more significantly + larger)
    current = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(current)
    draw.rectangle([50, 40, 75, 60], fill='black')  # Moved 10px right, 15px wider
    current_path = tmp_path / "current.png"
    current.save(current_path)
    
    return str(baseline_path), str(current_path)


@pytest.fixture
def identical_images(tmp_path):
    """Create two identical images for testing."""
    baseline = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(baseline)
    draw.rectangle([40, 40, 60, 60], fill='black')
    
    baseline_path = tmp_path / "baseline_same.png"
    current_path = tmp_path / "current_same.png"
    
    baseline.save(baseline_path)
    baseline.save(current_path)  # Save same image twice
    
    return str(baseline_path), str(current_path)


# ========================================
# TEST 1: VISUAL DIFF DETECTION
# ========================================

def test_visual_diff_detection(temp_vision_analyzer, sample_images):
    """
    Test that visual differences are detected between baseline and current.
    
    Expected:
        - Similarity < 1.0 (images are different)
        - diff_pixels > 0
        - Diff map saved
    """
    baseline_path, current_path = sample_images
    
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    
    # Assertions
    assert diff["similarity"] < 1.0, "Similarity should be less than 1.0 for different images"
    assert diff["diff_pixels"] > 0, "Should detect pixel differences"
    assert "diff_map_path" in diff
    assert diff["diff_map_path"] is not None
    assert os.path.exists(diff["diff_map_path"]), "Diff map should be saved"
    
    print(f"✅ Visual diff detected: {diff['similarity']:.4f} similarity, {diff['diff_percentage']:.2f}% changed")


def test_visual_diff_identical_images(temp_vision_analyzer, identical_images):
    """
    Test that identical images show high similarity.
    
    Expected:
        - Similarity = 1.0 or very close
        - diff_pixels = 0 or very small
    """
    baseline_path, current_path = identical_images
    
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    
    # Assertions
    assert diff["similarity"] >= 0.99, f"Identical images should have similarity >= 0.99, got {diff['similarity']}"
    assert diff["diff_pixels"] == 0 or diff["diff_pixels"] < 10, "Identical images should have minimal diff"
    
    print(f"✅ Identical images: {diff['similarity']:.4f} similarity")


# ========================================
# TEST 2: DETECT VISUAL ANOMALIES
# ========================================

def test_detect_visual_anomalies_with_differences(temp_vision_analyzer, sample_images):
    """
    Test that anomalies are detected when images differ significantly.
    
    Expected:
        - Anomalies list is not empty
        - Each anomaly has region, severity, description
    """
    baseline_path, current_path = sample_images
    
    anomalies = temp_vision_analyzer.detect_visual_anomalies(
        baseline_path,
        current_path,
        threshold=0.97  # Lower threshold to catch smaller diffs (sample images have ~98% similarity)
    )
    
    # Assertions
    assert len(anomalies) > 0, "Should detect anomalies for different images"
    
    anomaly = anomalies[0]
    assert "region" in anomaly
    assert "severity" in anomaly
    assert "description" in anomaly
    assert "confidence" in anomaly
    
    print(f"✅ Detected {len(anomalies)} anomalies: {anomaly['severity']} severity")


def test_detect_visual_anomalies_no_differences(temp_vision_analyzer, identical_images):
    """
    Test that no anomalies are detected for identical images.
    
    Expected:
        - Anomalies list is empty (similarity above threshold)
    """
    baseline_path, current_path = identical_images
    
    anomalies = temp_vision_analyzer.detect_visual_anomalies(
        baseline_path,
        current_path,
        threshold=0.95
    )
    
    # Assertions
    assert len(anomalies) == 0, "Should not detect anomalies for identical images"
    
    print(f"✅ No anomalies detected for identical images")


# ========================================
# TEST 3: LLM VISUAL ANALYSIS
# ========================================

def test_llm_visual_analysis(temp_vision_analyzer, sample_images):
    """
    Test that LLM can analyze visual differences.
    
    Expected:
        - Returns description from mocked LLM
        - Analysis includes elements_affected and suggested_action
    """
    baseline_path, current_path = sample_images
    
    # Create diff map first
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    diff_map_path = diff["diff_map_path"]
    
    # Analyze with LLM
    analysis = temp_vision_analyzer.analyze_with_llm(
        diff_map_path,
        "What UI elements changed in this screenshot?"
    )
    
    # Assertions
    assert "description" in analysis
    assert analysis["description"] != "", "LLM should return description"
    assert "elements_affected" in analysis
    assert "suggested_action" in analysis
    
    print(f"✅ LLM analysis: {analysis['description'][:50]}...")


def test_llm_visual_analysis_caching(temp_vision_analyzer, sample_images):
    """
    Test that LLM analysis results are cached.
    
    Expected:
        - First call: LLM is called
        - Second call: Result from cache (LLM not called again)
    """
    baseline_path, current_path = sample_images
    
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    diff_map_path = diff["diff_map_path"]
    
    # First call
    analysis1 = temp_vision_analyzer.analyze_with_llm(diff_map_path, "Test question")
    
    # Second call (should hit cache)
    analysis2 = temp_vision_analyzer.analyze_with_llm(diff_map_path, "Test question")
    
    # Assertions
    assert analysis1 == analysis2, "Cached result should match original"
    assert temp_vision_analyzer.ai_gateway.ask_vision.call_count == 1, "LLM should be called only once (caching)"
    
    print(f"✅ LLM analysis cached successfully")


# ========================================
# TEST 4: SUGGEST LOCATOR FROM VISUALS
# ========================================

def test_suggest_locator_from_visuals(temp_vision_analyzer, sample_images):
    """
    Test that locator suggestions work from visual differences.
    
    Expected:
        - Returns a suggested locator string
        - Locator is based on context hint and engine
    """
    baseline_path, current_path = sample_images
    
    # Detect anomalies
    anomalies = temp_vision_analyzer.detect_visual_anomalies(
        baseline_path,
        current_path,
        threshold=0.97  # Match the threshold used in other tests
    )
    
    # Suggest locator
    locator = temp_vision_analyzer.suggest_locator_from_visuals(
        anomalies,
        context_hint="Submit button",
        engine="Playwright"
    )
    
    # Assertions
    assert locator is not None, "Should suggest a locator"
    assert isinstance(locator, str), "Locator should be a string"
    assert len(locator) > 0, "Locator should not be empty"
    
    print(f"✅ Suggested locator: {locator}")


def test_suggest_locator_no_anomalies(temp_vision_analyzer):
    """
    Test that no locator is suggested when there are no anomalies.
    
    Expected:
        - Returns None (no visual differences to work with)
    """
    locator = temp_vision_analyzer.suggest_locator_from_visuals(
        [],  # Empty anomalies list
        context_hint="Button",
        engine="Playwright"
    )
    
    # Assertions
    assert locator is None, "Should return None when no anomalies"
    
    print(f"✅ No locator suggested for no anomalies")


# ========================================
# TEST 5: VISUAL FALLBACK IN AI HEALER
# ========================================

def test_visual_fallback_healing_integration(tmp_path, sample_images):
    """
    Test that AIHealer uses visual fallback when AI healing fails.
    
    Expected:
        - AI healing fails (mocked)
        - Heuristic fallback fails
        - Visual fallback succeeds
        - healing_source = "vision"
    """
    baseline_path, current_path = sample_images
    
    log_path = tmp_path / "healing_log.json"
    cache_path = tmp_path / "healing_cache.json"
    
    # Create AIHealer with vision enabled
    healer = AIHealer(
        log_path=str(log_path),
        cache_path=str(cache_path),
        enable_vision=True,
        baseline_screenshot=baseline_path,
        current_screenshot=current_path
    )
    
    # Mock AI to always fail (return same locator)
    with patch.object(healer.ai, 'ask', return_value="#failed-locator"):
        # Mock vision analyzer to return a locator
        if healer.vision_analyzer:
            with patch.object(
                healer.vision_analyzer,
                'suggest_locator_from_visuals',
                return_value="button[type='submit']"
            ):
                mock_page = Mock()
                # Mock page.content() to return string (required for _build_prompt)
                mock_page.content = Mock(return_value="<html><body><button>Submit</button></body></html>")
                
                # Attempt healing
                new_locator = healer.heal_locator(
                    mock_page,
                    failed_locator="#failed-locator",
                    context_hint="Submit button",
                    engine="Playwright"
                )
                
                # Assertions
                assert new_locator != "#failed-locator", "Should heal via vision fallback"
                assert new_locator == "button[type='submit']", "Should return vision-suggested locator"
                
                print(f"✅ Visual fallback healing succeeded: {new_locator}")
        else:
            pytest.skip("VisionAnalyzer not available")


def test_visual_fallback_disabled(tmp_path):
    """
    Test that visual fallback doesn't activate when disabled.
    
    Expected:
        - Vision analyzer is None
        - No visual fallback attempted
    """
    log_path = tmp_path / "healing_log.json"
    cache_path = tmp_path / "healing_cache.json"
    
    # Create AIHealer WITHOUT vision enabled
    healer = AIHealer(
        log_path=str(log_path),
        cache_path=str(cache_path),
        enable_vision=False
    )
    
    # Assertions
    assert healer.vision_analyzer is None, "Vision analyzer should be None when disabled"
    assert not healer.enable_vision, "Vision should be disabled"
    
    print(f"✅ Vision fallback correctly disabled")


# ========================================
# TEST 6: CACHE MANAGEMENT
# ========================================

def test_vision_cache_stats(temp_vision_analyzer, sample_images):
    """
    Test that cache statistics are tracked correctly.
    
    Expected:
        - get_cache_stats returns cache size and keys
    """
    baseline_path, current_path = sample_images
    
    # Perform some analysis to populate cache
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    temp_vision_analyzer.analyze_with_llm(diff["diff_map_path"], "Test")
    
    stats = temp_vision_analyzer.get_cache_stats()
    
    # Assertions
    assert "cache_size" in stats
    assert stats["cache_size"] >= 0
    assert "cache_file" in stats
    
    print(f"✅ Cache stats: {stats['cache_size']} entries")


def test_vision_clear_cache(temp_vision_analyzer, sample_images):
    """
    Test that cache can be cleared.
    
    Expected:
        - After clear_cache(), cache size = 0
    """
    baseline_path, current_path = sample_images
    
    # Add something to cache
    diff = temp_vision_analyzer.compare_images(baseline_path, current_path)
    temp_vision_analyzer.analyze_with_llm(diff["diff_map_path"], "Test")
    
    # Clear cache
    temp_vision_analyzer.clear_cache()
    
    stats = temp_vision_analyzer.get_cache_stats()
    
    # Assertions
    assert stats["cache_size"] == 0, "Cache should be empty after clear"
    
    print(f"✅ Cache cleared successfully")


# ========================================
# RUN TESTS
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
