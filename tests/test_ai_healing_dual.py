"""
tests/test_ai_healing_dual.py
---------------------------------------------------
Phase 2 (extended): AI-Healing demonstration with
both Playwright and Selenium on the same page.
---------------------------------------------------
"""

import pytest
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from core.ai_healer import AIHealer


def test_ai_healing_playwright_and_selenium(tmp_path):
    healer = AIHealer(log_path="logs/healing_log.json")

    # Use local HTML to avoid network/SSL issues
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>HTML Forms Test</title></head>
    <body>
        <h1>HTML Forms</h1>
        <form action="/action_page.php">
            <label for="fname">First name:</label><br>
            <input type="text" id="fname" name="fname" value="John"><br>
            <label for="lname">Last name:</label><br>
            <input type="text" id="lname" name="lname" value="Doe"><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    
    failed_locator = "input#wrong_id"
    context_hint = "Find the 'First name' input box"

    print("\n" + "="*80)
    print("=== 🎭 PLAYWRIGHT SECTION ===")
    print("="*80)
    
    with sync_playwright() as p:
        # Launch with SSL bypass for corporate networks
        browser = p.chromium.launch(
            headless=True,
            args=['--ignore-certificate-errors']
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Use local HTML content
        page.set_content(html_content)
        print("✅ Page loaded (local HTML)")

        try:
            page.locator(failed_locator).click(timeout=2000)
        except Exception as e:
            print(f"❌ Playwright failed: {failed_locator}")
            print(f"   Error: {str(e)[:80]}...")
            
            print("🤖 Triggering AI-Healer...")
            healed_locator = healer.heal_locator(page, failed_locator, context_hint)
            print(f"✨ AI suggested (Playwright): {healed_locator}")
            
            page.locator(healed_locator).fill("John (PW-Healed)")
            print("✅ Playwright healed successfully!")

        browser.close()

    print("\n" + "="*80)
    print("=== 🐍 SELENIUM SECTION ===")
    print("="*80)
    
    # Configure Chrome options for SSL bypass
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--headless')  # Run headless
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Load the same HTML content in Selenium
    driver.get("data:text/html;charset=utf-8," + html_content)
    print("✅ Page loaded (local HTML)")

    try:
        driver.find_element(By.CSS_SELECTOR, failed_locator).click()
    except Exception as e:
        print(f"❌ Selenium failed: {failed_locator}")
        print(f"   Error: {str(e)[:80]}...")

        print("🤖 Triggering AI-Healer...")
        # Use Playwright page HTML for healing (same logic)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content)
            healed_locator = healer.heal_locator(page, failed_locator, context_hint)
            browser.close()

        print(f"✨ AI suggested (Selenium): {healed_locator}")

        element = driver.find_element(By.CSS_SELECTOR, healed_locator)
        element.send_keys("John (SEL-Healed)")
        print("✅ Selenium healed successfully!")

    driver.quit()

    print("\n" + "="*80)
    print("📝 HEALING LOG:")
    print("="*80)
    healer.show_recent_healings(limit=5)
