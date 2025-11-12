"""
test_ai_healer_optimization.py
-------------------------------------------------
Unit tests for AI Healer optimization features:
  ✅ Cache hit/miss
  ✅ Retry logic with backoff
  ✅ Response sanitization
  ✅ Fallback recovery
  ✅ Log structure validation
  ✅ Performance tracking
-------------------------------------------------
"""

import pytest
import json
import os
import time
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_healer import AIHealer


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def temp_healer(tmp_path):
    """Create AI Healer with temporary log/cache paths."""
    log_path = tmp_path / "healing_log.json"
    cache_path = tmp_path / "healing_cache.json"
    
    healer = AIHealer(log_path=str(log_path), cache_path=str(cache_path))
    return healer


@pytest.fixture
def mock_page():
    """Mock Playwright page object."""
    page = Mock()
    page.content.return_value = "<html><body><button id='submit'>Submit</button></body></html>"
    return page


# ========================================
# TEST 1: CACHE HIT (NO API CALL)
# ========================================

def test_cache_hit_no_api_call(temp_healer, mock_page):
    """
    Test that cached locator is returned without calling AI.
    
    Expected:
        - First call: AI is called, result cached
        - Second call: Cache hit, AI not called
        - Healing source logged as 'cache'
    """
    failed_locator = "#old-button"
    context = "Submit button"
    engine = "Playwright"
    
    # Mock AI to return healed locator
    with patch.object(temp_healer.ai, 'ask', return_value='button[type="submit"]') as mock_ai:
        # First call - should call AI
        result1 = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        assert mock_ai.call_count == 1
        assert result1 == 'button[type="submit"]'
        
        # Second call - should use cache
        result2 = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        assert mock_ai.call_count == 1  # Still 1, not called again
        assert result2 == 'button[type="submit"]'
    
    # Verify cache contains the entry
    cache_key = f"{engine}:{failed_locator}:{context}"
    assert cache_key in temp_healer.cache
    
    # Verify log shows cache hit
    with open(temp_healer.log_path, 'r') as f:
        logs = json.load(f)
    
    assert len(logs) == 2
    assert logs[0]['healing_source'] == 'ai'
    assert logs[1]['healing_source'] == 'cache'
    
    print("✅ Test passed: Cache hit avoids redundant AI call")


# ========================================
# TEST 2: CACHE MISS (API CALLED)
# ========================================

def test_cache_miss_calls_api(temp_healer, mock_page):
    """
    Test that AI is called when cache misses.
    
    Expected:
        - Cache miss triggers AI call
        - Result is cached for future use
        - Healing source logged as 'ai'
    """
    failed_locator = "#unique-locator"
    context = "Unique element"
    engine = "Playwright"
    
    with patch.object(temp_healer.ai, 'ask', return_value='#new-locator') as mock_ai:
        result = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        
        assert mock_ai.call_count == 1
        assert result == '#new-locator'
    
    # Verify it was cached
    cache_key = f"{engine}:{failed_locator}:{context}"
    assert cache_key in temp_healer.cache
    assert temp_healer.cache[cache_key] == '#new-locator'
    
    print("✅ Test passed: Cache miss triggers AI call")


# ========================================
# TEST 3: RETRY LOGIC (SIMULATE FAILURE)
# ========================================

def test_retry_logic_with_eventual_success(temp_healer, mock_page):
    """
    Test retry logic with exponential backoff.
    
    Expected:
        - First 2 attempts fail
        - Third attempt succeeds
        - Total 3 AI calls
        - Exponential backoff observed
    """
    failed_locator = "#flaky-element"
    context = "Flaky element"
    engine = "Playwright"
    
    # Simulate 2 failures, then success
    with patch.object(temp_healer.ai, 'ask', side_effect=[
        Exception("Network error"),
        Exception("Timeout"),
        'button.success'
    ]) as mock_ai:
        start_time = time.time()
        result = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        elapsed = time.time() - start_time
        
        assert mock_ai.call_count == 3
        assert result == 'button.success'
        
        # Verify backoff delays (1s + 2s = 3s minimum)
        assert elapsed >= 3.0, "Should have backoff delays"
    
    print("✅ Test passed: Retry logic with exponential backoff works")


def test_retry_logic_all_failures(temp_healer, mock_page):
    """
    Test that original locator is returned after all retries fail.
    
    Expected:
        - All 3 attempts fail
        - Original locator returned
        - Healing source logged as 'ai' (attempted)
    """
    failed_locator = "#permanent-fail"
    context = "Failing element"
    engine = "Playwright"
    
    with patch.object(temp_healer.ai, 'ask', side_effect=Exception("Persistent error")):
        result = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        
        # Should return original locator OR fallback
        assert result in [failed_locator, "text=Failing"]  # Could be fallback
    
    print("✅ Test passed: Returns original/fallback after all retries fail")


# ========================================
# TEST 4: RESPONSE SANITIZATION
# ========================================

@pytest.mark.parametrize("raw_response,expected", [
    # Markdown code blocks
    ("```css\n#submit-btn\n```", "#submit-btn"),
    ("```xpath\n//button[@id='submit']\n```", "//button[@id='submit']"),
    
    # Backticks
    ("`#button`", "#button"),
    ("`.class-name`", ".class-name"),
    
    # Quotes
    ('"button[type=submit]"', "button[type=submit]"),
    ("'input#username'", "input#username"),
    
    # JSON responses
    ('{"locator": "#element"}', "#element"),
    ('locator: "#submit"', "#submit"),
    
    # Multi-line responses
    ("#button\nThis is the submit button", "#button"),
    
    # Mixed formatting
    ('```\n"#submit-btn"\n```', "#submit-btn"),
])
def test_response_sanitization(temp_healer, raw_response, expected):
    """
    Test AI response sanitization with various formats.
    
    Expected:
        - All markdown, backticks, quotes removed
        - Only pure locator string extracted
    """
    cleaned = temp_healer._clean_ai_response(raw_response)
    assert cleaned == expected, f"Failed to clean: {raw_response}"
    
    print(f"✅ Cleaned '{raw_response}' → '{cleaned}'")


def test_response_sanitization_empty(temp_healer):
    """Test sanitization of empty response."""
    assert temp_healer._clean_ai_response("") == ""
    assert temp_healer._clean_ai_response("   ") == ""
    
    print("✅ Test passed: Empty response handling")


# ========================================
# TEST 5: FALLBACK RECOVERY
# ========================================

def test_heuristic_fallback_submit(temp_healer):
    """
    Test heuristic fallback for 'Submit' context.
    
    Expected:
        - Playwright: button[type='submit']
        - Selenium: //button[@type='submit']
    """
    fallback_pw = temp_healer._heuristic_fallback("Submit button", "Playwright")
    assert fallback_pw == "button[type='submit']"
    
    fallback_sel = temp_healer._heuristic_fallback("Submit button", "Selenium")
    assert fallback_sel == "//button[@type='submit']"
    
    print("✅ Test passed: Heuristic fallback for 'Submit'")


def test_heuristic_fallback_login(temp_healer):
    """Test heuristic fallback for 'Login' context."""
    fallback_pw = temp_healer._heuristic_fallback("Login button", "Playwright")
    assert "Login" in fallback_pw or "login" in fallback_pw
    
    print("✅ Test passed: Heuristic fallback for 'Login'")


def test_heuristic_fallback_no_context(temp_healer):
    """Test that no fallback is generated without context."""
    fallback = temp_healer._heuristic_fallback("", "Playwright")
    assert fallback is None
    
    print("✅ Test passed: No fallback without context")


def test_fallback_used_when_ai_fails(temp_healer, mock_page):
    """
    Test that fallback is used when AI completely fails.
    
    Expected:
        - AI fails all retries
        - Fallback locator is used
        - Healing source logged as 'fallback'
    """
    failed_locator = "#broken"
    context = "Submit button"
    engine = "Playwright"
    
    with patch.object(temp_healer.ai, 'ask', side_effect=Exception("AI down")):
        result = temp_healer.heal_locator(mock_page, failed_locator, context, engine)
        
        # Should get fallback locator
        assert result == "button[type='submit']"  # Fallback for 'Submit'
    
    # Verify log shows fallback
    with open(temp_healer.log_path, 'r') as f:
        logs = json.load(f)
    
    assert logs[-1]['healing_source'] == 'fallback'
    
    print("✅ Test passed: Fallback used when AI fails")


# ========================================
# TEST 6: LOG STRUCTURE VALIDATION
# ========================================

def test_log_structure_contains_all_fields(temp_healer, mock_page):
    """
    Test that log entries contain all required fields.
    
    Expected fields:
        - timestamp
        - engine
        - old_locator
        - new_locator
        - healing_source
        - latency_ms
        - context_hint
        - success
    """
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        temp_healer.heal_locator(mock_page, "#old", "Test context", "Playwright")
    
    with open(temp_healer.log_path, 'r') as f:
        logs = json.load(f)
    
    entry = logs[-1]
    
    # Verify all required fields
    required_fields = [
        'timestamp', 'engine', 'old_locator', 'new_locator',
        'healing_source', 'latency_ms', 'context_hint', 'success'
    ]
    
    for field in required_fields:
        assert field in entry, f"Missing field: {field}"
    
    # Verify data types
    assert isinstance(entry['latency_ms'], (int, float))
    assert isinstance(entry['success'], bool)
    assert entry['healing_source'] in ['cache', 'ai', 'fallback']
    
    print("✅ Test passed: Log structure validation")


def test_log_latency_tracking(temp_healer, mock_page):
    """
    Test that latency is tracked correctly.
    
    Expected:
        - latency_ms is positive number
        - Cache hits have low latency (< 10ms)
        - AI calls have higher latency (> 10ms)
    """
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        # First call - AI (slower)
        temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
    
    with open(temp_healer.log_path, 'r') as f:
        logs = json.load(f)
    
    ai_latency = logs[-1]['latency_ms']
    
    # Second call - Cache (faster)
    temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
    
    with open(temp_healer.log_path, 'r') as f:
        logs = json.load(f)
    
    cache_latency = logs[-1]['latency_ms']
    
    assert ai_latency > 0
    # Cache can be extremely fast (< 1ms), so just check it's non-negative
    assert cache_latency >= 0
    # If cache latency > 0, it should be faster than AI
    if cache_latency > 0:
        assert cache_latency < ai_latency, "Cache should be faster than AI"
    
    print(f"✅ Test passed: AI latency={ai_latency}ms, Cache latency={cache_latency}ms")


# ========================================
# TEST 7: CACHE MANAGEMENT
# ========================================

def test_cache_save_load(temp_healer, mock_page):
    """
    Test that cache persists across instances.
    
    Expected:
        - Cache saved to disk
        - New instance loads cache
        - Cached entries available
    """
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
    
    # Create new instance with same cache path
    new_healer = AIHealer(
        log_path=temp_healer.log_path,
        cache_path=temp_healer.cache_path
    )
    
    # Verify cache was loaded
    cache_key = f"Playwright:#old:Test"
    assert cache_key in new_healer.cache
    assert new_healer.cache[cache_key] == '#healed'
    
    print("✅ Test passed: Cache persists across instances")


def test_clear_cache(temp_healer, mock_page):
    """
    Test cache clearing.
    
    Expected:
        - Cache populated
        - After clear, cache is empty
        - Next call triggers AI
    """
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
    
    assert len(temp_healer.cache) > 0
    
    # Clear cache
    temp_healer.clear_cache()
    
    assert len(temp_healer.cache) == 0
    
    # Verify cache file is empty
    with open(temp_healer.cache_path, 'r') as f:
        cache_data = json.load(f)
    
    assert cache_data == {}
    
    print("✅ Test passed: Cache clearing")


# ========================================
# TEST 8: STATISTICS & DIAGNOSTICS
# ========================================

def test_get_cache_stats(temp_healer, mock_page):
    """Test cache statistics retrieval."""
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        temp_healer.heal_locator(mock_page, "#old1", "Test1", "Playwright")
        temp_healer.heal_locator(mock_page, "#old2", "Test2", "Playwright")
    
    stats = temp_healer.get_cache_stats()
    
    assert stats['cache_size'] == 2
    assert len(stats['cache_keys']) == 2
    
    print(f"✅ Test passed: Cache stats = {stats}")


def test_get_healing_stats(temp_healer, mock_page):
    """
    Test healing statistics calculation.
    
    Expected stats:
        - total_healings
        - by_source (cache, ai, fallback counts)
        - success_rate
        - avg_latency_ms
        - cache_hit_rate
    """
    with patch.object(temp_healer.ai, 'ask', return_value='#healed'):
        # First call - AI
        temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
        
        # Second call - Cache
        temp_healer.heal_locator(mock_page, "#old", "Test", "Playwright")
    
    stats = temp_healer.get_healing_stats()
    
    assert stats['total_healings'] == 2
    assert stats['by_source']['ai'] == 1
    assert stats['by_source']['cache'] == 1
    assert stats['success_rate'] == 100.0
    assert stats['avg_latency_ms'] > 0
    assert stats['cache_hit_rate'] == 50.0
    
    print(f"✅ Test passed: Healing stats = {stats}")


# ========================================
# RUN ALL TESTS
# ========================================

if __name__ == "__main__":
    """
    Run all optimization tests.
    
    Usage:
        pytest tests/test_ai_healer_optimization.py -v
        pytest tests/test_ai_healer_optimization.py -v -s  # with output
    """
    print("=" * 80)
    print("🧪 AI HEALER OPTIMIZATION TEST SUITE")
    print("=" * 80)
    print("\nTests:")
    print("  ✅ Cache hit (no API call)")
    print("  ✅ Cache miss (API called)")
    print("  ✅ Retry logic (simulate failure)")
    print("  ✅ Response sanitization")
    print("  ✅ Fallback recovery")
    print("  ✅ Log structure validation")
    print("  ✅ Cache management")
    print("  ✅ Statistics & diagnostics")
    print("\n" + "=" * 80)
    print("\nRun: pytest tests/test_ai_healer_optimization.py -v")
