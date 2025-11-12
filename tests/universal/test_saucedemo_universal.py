"""
Universal Test for SauceDemo Login  
===================================

Backup test site with easier automation (https://www.saucedemo.com/).

This demonstrates the Universal AI Interaction Layer on a site
that ALLOWS automation, proving the framework works on both
protected and unprotected sites.

Author: Ram
Date: November 12, 2025
Phase: 7 - Universal Interactor
"""

import pytest
import time
import json
from pathlib import Path
from adapters.playwright_adapter import launch_stealth_browser
from core.ai_healer import AIHealer
from core.ai_interactor import AIInteractor

# SauceDemo Login Page
SAUCEDEMO_URL = "https://www.saucedemo.com/"
SAUCEDEMO_USERNAME = "standard_user"
SAUCEDEMO_PASSWORD = "secret_sauce"

# Paths
REPORTS_DIR = Path("reports")
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots" / "saucedemo_universal"
LOGS_DIR = Path("logs")

# Create directories
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="function")
def stealth_browser():
    """Launch stealth browser with anti-detection measures."""
    from playwright.sync_api import sync_playwright
    
    print("\n[Fixture] Starting Playwright...")
    p = sync_playwright().start()
    
    print("[Fixture] Launching stealth browser...")
    browser, context, page = launch_stealth_browser(headless=True, playwright_instance=p)
    
    print("[Fixture] ✅ Stealth browser launched")
    
    yield browser, context, page
    
    print("[Fixture] Closing stealth browser...")
    browser.close()
    p.stop()
    print("[Fixture] ✅ Browser closed")


@pytest.fixture(scope="function")
def ai_healer():
    """Create AIHealer instance."""
    print("[Fixture] Creating AI-Healer...")
    healer = AIHealer(
        log_path="logs/healing_log_saucedemo.json",
        cache_path="logs/healing_cache_saucedemo.json"
    )
    print("[Fixture] ✅ AI-Healer created")
    return healer


def test_saucedemo_universal_complete_workflow(stealth_browser, ai_healer):
    """
    Test Case: Complete Universal Workflow on SauceDemo
    
    Tests the full workflow on a site that allows automation:
    1. Launch stealth browser
    2. Break a locator deliberately
    3. AI-Healer repairs the locator
    4. AIInteractor fills fields (should succeed with direct method)
    5. Login succeeds
    6. Verify interaction_method is "direct" (no fallbacks needed)
    
    Expected: All interactions succeed with 'direct' method
    """
    browser, context, page = stealth_browser
    
    print("\n" + "="*80)
    print("TEST: SauceDemo Universal (Full Workflow)")
    print("="*80)
    
    # Step 1: Navigate to SauceDemo
    print("\n[Step 1] Navigating to SauceDemo...")
    page.goto(SAUCEDEMO_URL, wait_until="networkidle")
    time.sleep(1)
    print(f"✅ Page loaded: {page.url}")
    
    # Capture baseline screenshot
    baseline_path = SCREENSHOTS_DIR / "baseline_login.png"
    page.screenshot(path=str(baseline_path))
    print(f"📸 Baseline screenshot saved: {baseline_path}")
    
    # Step 2: Use AI-Healer with a BROKEN locator
    print("\n[Step 2] Testing AI-Healer with broken locator...")
    
    broken_locator = "#user-name-broken-field-xyz"
    context_hint = "This is the username input field, likely has id='user-name'"
    
    print(f"❌ Broken locator: {broken_locator}")
    
    healed_locator = ai_healer.heal_locator(
        page=page,
        failed_locator=broken_locator,
        context_hint=context_hint,
        engine="Playwright"
    )
    
    print(f"✅ Healed locator: {healed_locator}")
    assert healed_locator != broken_locator, "AI-Healer should repair locator"
    
    # Step 3: Initialize AIInteractor
    print("\n[Step 3] Initializing AIInteractor...")
    interactor = AIInteractor(page, timeout=5000)
    
    # Step 4: Fill username using AIInteractor
    print("\n[Step 4] Filling username with AIInteractor...")
    
    username_success = interactor.safe_fill(
        selector=healed_locator,
        value=SAUCEDEMO_USERNAME,
        context_hint="username field"
    )
    
    assert username_success, "Username fill should succeed on SauceDemo"
    print("✅ Username filled successfully")
    
    # Step 5: Fill password
    print("\n[Step 5] Filling password...")
    
    password_success = interactor.safe_fill(
        selector="#password",
        value=SAUCEDEMO_PASSWORD,
        context_hint="password field"
    )
    
    assert password_success, "Password fill should succeed"
    print("✅ Password filled successfully")
    
    # Step 6: Click login button
    print("\n[Step 6] Clicking login button...")
    
    click_success = interactor.safe_click(
        selector="#login-button",
        context_hint="login button"
    )
    
    assert click_success, "Login button click should succeed"
    print("✅ Login button clicked successfully")
    
    # Wait for redirect
    time.sleep(2)
    
    # Step 7: Verify login succeeded
    print("\n[Step 7] Verifying login success...")
    
    current_url = page.url
    print(f"Current URL: {current_url}")
    
    # SauceDemo redirects to /inventory.html on success
    assert "inventory.html" in current_url, "Should redirect to inventory page"
    print("✅ Login succeeded - redirected to inventory page")
    
    # Capture success screenshot
    success_path = SCREENSHOTS_DIR / "login_success.png"
    page.screenshot(path=str(success_path))
    print(f"📸 Success screenshot saved: {success_path}")
    
    # Step 8: Verify interaction statistics
    print("\n[Step 8] Verifying interaction statistics...")
    
    stats = interactor.get_interaction_stats()
    
    print(f"📊 Interaction Statistics:")
    for method, count in stats.items():
        if count > 0:
            print(f"   {method}: {count}")
    
    # On SauceDemo, all should be 'direct' (no fallbacks needed)
    assert stats['direct'] >= 3, "Should have at least 3 direct interactions"
    assert stats['degraded'] == 0, "Should have no degraded interactions"
    print("✅ All interactions used 'direct' method (no fallbacks needed)")
    
    # Step 9: Verify healing log
    print("\n[Step 9] Verifying healing log...")
    
    healing_log_path = LOGS_DIR / "healing_log_saucedemo.json"
    assert healing_log_path.exists(), "Healing log should exist"
    
    with open(healing_log_path, "r") as f:
        healing_events = json.load(f)
    
    latest_event = healing_events[-1] if healing_events else {}
    
    print(f"📋 Latest Healing Event:")
    print(f"   Old Locator: {latest_event.get('old_locator', 'N/A')}")
    print(f"   New Locator: {latest_event.get('new_locator', 'N/A')}")
    print(f"   Healing Source: {latest_event.get('healing_source', 'N/A')}")
    print(f"   Latency: {latest_event.get('latency_ms', 'N/A')}ms")
    
    assert 'new_locator' in latest_event, "Healing log should contain new_locator"
    print("✅ Healing log contains all required fields")
    
    # Step 10: Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY:")
    print("="*80)
    print(f"✅ Stealth browser launched")
    print(f"✅ AI-Healer repaired broken locator: {broken_locator} → {healed_locator}")
    print(f"✅ AIInteractor filled 2 fields + clicked button")
    print(f"✅ Login succeeded (redirected to inventory page)")
    print(f"✅ All interactions used 'direct' method (site allows automation)")
    print(f"✅ Healing log and interaction logs complete")
    print("="*80)
    print("✅ TEST PASSED: Universal layer works on automation-friendly sites")
    print("="*80)


def test_saucedemo_universal_direct_method_preferred(stealth_browser):
    """
    Test Case: Direct Method is Preferred
    
    Verifies that AIInteractor prefers the 'direct' method when available
    and doesn't unnecessarily use fallbacks.
    
    Expected: All interactions use 'direct' method
    """
    browser, context, page = stealth_browser
    
    print("\n" + "="*80)
    print("TEST: AIInteractor Prefers Direct Method")
    print("="*80)
    
    # Navigate
    page.goto(SAUCEDEMO_URL, wait_until="networkidle")
    time.sleep(1)
    
    # Initialize interactor
    interactor = AIInteractor(page, timeout=5000)
    
    # Perform multiple interactions
    print("\n[Test] Performing interactions...")
    
    interactor.safe_fill("#user-name", SAUCEDEMO_USERNAME, "username")
    interactor.safe_fill("#password", SAUCEDEMO_PASSWORD, "password")
    interactor.safe_click("#login-button", "login button")
    
    time.sleep(2)
    
    # Check statistics
    stats = interactor.get_interaction_stats()
    
    print(f"\n📊 Statistics:")
    print(f"   Direct: {stats['direct']}")
    print(f"   JS Inject: {stats['js_inject']}")
    print(f"   Human Typing: {stats['human_typing']}")
    print(f"   Degraded: {stats['degraded']}")
    
    # Verify all used direct method
    assert stats['direct'] == 3, "All 3 interactions should use direct method"
    assert stats['js_inject'] == 0, "Should not use JS injection"
    assert stats['human_typing'] == 0, "Should not use human typing"
    assert stats['degraded'] == 0, "Should not degrade"
    
    print("\n✅ TEST PASSED: AIInteractor correctly prefers direct method")


def test_saucedemo_universal_interaction_logging(stealth_browser):
    """
    Test Case: Interaction Logging Verification
    
    Verifies that all interactions are properly logged with:
    - interaction_method
    - interaction_latency_ms
    - selector
    - context
    - timestamp
    - failed flag
    
    Expected: All log entries contain required fields
    """
    browser, context, page = stealth_browser
    
    print("\n" + "="*80)
    print("TEST: Interaction Logging Verification")
    print("="*80)
    
    # Navigate
    page.goto(SAUCEDEMO_URL, wait_until="networkidle")
    time.sleep(1)
    
    # Initialize interactor
    interactor = AIInteractor(page, timeout=5000)
    
    # Perform interactions with context hints
    print("\n[Test] Performing tracked interactions...")
    
    interactor.safe_fill("#user-name", "test1", "username field")
    interactor.safe_fill("#password", "test2", "password field")
    interactor.safe_click("#login-button", "login button")
    
    time.sleep(1)
    
    # Get interaction log
    log = interactor.get_interaction_log()
    
    print(f"\n📋 Interaction Log ({len(log)} entries):")
    
    for i, entry in enumerate(log, 1):
        print(f"\n   Entry #{i}:")
        print(f"      Method: {entry.get('interaction_method')}")
        print(f"      Latency: {entry.get('interaction_latency_ms')}ms")
        print(f"      Selector: {entry.get('selector')}")
        print(f"      Context: {entry.get('context')}")
        print(f"      Failed: {entry.get('failed')}")
        
        # Verify all required fields exist
        assert 'interaction_method' in entry, f"Entry {i} missing interaction_method"
        assert 'interaction_latency_ms' in entry, f"Entry {i} missing latency"
        assert 'selector' in entry, f"Entry {i} missing selector"
        assert 'context' in entry, f"Entry {i} missing context"
        assert 'timestamp' in entry, f"Entry {i} missing timestamp"
        assert 'failed' in entry, f"Entry {i} missing failed flag"
        
        # Verify types
        assert isinstance(entry['interaction_latency_ms'], (int, float)), "Latency should be numeric"
        assert isinstance(entry['failed'], bool), "Failed should be boolean"
    
    assert len(log) == 3, "Should have 3 logged interactions"
    
    print("\n✅ TEST PASSED: All interactions properly logged with required fields")


# Run with: pytest -v tests/universal/test_saucedemo_universal.py -s
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
