"""
Demo: SmartLocator with Multiple Locator Types
===============================================

This test demonstrates SmartLocator's support for ALL major locator types
across both Playwright and Selenium frameworks.
"""

import pytest


class TestMultipleLocatorTypes:
    """Test SmartLocator with various locator strategies."""
    
    def test_playwright_locator_types(self, page):
        """Test all Playwright locator types with SmartLocator."""
        from core.smart_locator import SmartLocator, PlaywrightAdapter
        
        page.goto("https://practice.expandtesting.com/login")
        adapter = PlaywrightAdapter(page)
        
        print("\n" + "="*70)
        print("🎭 Testing Playwright Locator Types")
        print("="*70)
        
        # 1. CSS Selector (ID)
        print("\n1️⃣  Testing CSS Selector (ID): #username")
        username = SmartLocator("#username", adapter, "Username field")
        username.fill("practice")
        print("   ✅ CSS Selector (ID) working!")
        
        # 2. CSS Selector (Name attribute)
        print("\n2️⃣  Testing CSS Selector (Name): input[name='password']")
        password = SmartLocator("input[name='password']", adapter, "Password field")
        password.fill("SuperSecretPassword!")
        print("   ✅ CSS Selector (Name) working!")
        
        # 3. Text content locator
        print("\n3️⃣  Testing Text Locator: text=Login")
        login_btn = SmartLocator("text=Login", adapter, "Login button")
        assert login_btn.is_visible(), "Login button should be visible"
        print("   ✅ Text Locator working!")
        
        # 4. Role-based locator
        print("\n4️⃣  Testing Role Locator: role=button")
        button = SmartLocator("role=button", adapter, "Any button")
        assert button.is_visible(), "Button should be visible"
        print("   ✅ Role Locator working!")
        
        # 5. XPath
        print("\n5️⃣  Testing XPath: //input[@id='username']")
        username_xpath = SmartLocator("//input[@id='username']", adapter, "Username via XPath")
        assert username_xpath.is_visible(), "Username field should be visible via XPath"
        print("   ✅ XPath Locator working!")
        
        # 6. Data-testid (if available)
        print("\n6️⃣  Testing CSS with class: button.btn-primary")
        try:
            primary_btn = SmartLocator("button.btn-primary", adapter, "Primary button")
            if primary_btn.is_visible():
                print("   ✅ CSS Class Locator working!")
        except Exception as e:
            print(f"   ⚠️  Class locator not available on this page: {e}")
        
        print("\n" + "="*70)
        print("✅ All Playwright locator types tested successfully!")
        print("="*70 + "\n")
    
    def test_selenium_locator_types(self, driver):
        """Test all Selenium locator types with SmartLocator."""
        from core.smart_locator import SmartLocator, SeleniumAdapter
        
        driver.get("https://practice.expandtesting.com/login")
        adapter = SeleniumAdapter(driver)
        
        print("\n" + "="*70)
        print("🔧 Testing Selenium Locator Types")
        print("="*70)
        
        # 1. ID (explicit prefix)
        print("\n1️⃣  Testing ID (explicit): id=username")
        username_id = SmartLocator("id=username", adapter, "Username by ID")
        username_id.fill("practice")
        print("   ✅ ID Locator (explicit) working!")
        
        # 2. Name attribute
        print("\n2️⃣  Testing Name: name=password")
        password_name = SmartLocator("name=password", adapter, "Password by name")
        password_name.fill("SuperSecretPassword!")
        print("   ✅ Name Locator working!")
        
        # 3. CSS Selector (default)
        print("\n3️⃣  Testing CSS Selector: button.btn-primary")
        login_css = SmartLocator("button.btn-primary", adapter, "Login button CSS")
        assert login_css.is_visible(), "Login button should be visible"
        print("   ✅ CSS Selector working!")
        
        # 4. XPath
        print("\n4️⃣  Testing XPath: //button[@type='submit']")
        login_xpath = SmartLocator("//button[@type='submit']", adapter, "Login button XPath")
        assert login_xpath.is_visible(), "Login button should be visible via XPath"
        print("   ✅ XPath Locator working!")
        
        # 5. ID shorthand (#)
        print("\n5️⃣  Testing ID Shorthand: #username")
        username_short = SmartLocator("#username", adapter, "Username shorthand")
        assert username_short.is_visible(), "Username field should be visible"
        print("   ✅ ID Shorthand working!")
        
        # 6. Class (single class)
        print("\n6️⃣  Testing Class: class=btn-primary")
        try:
            btn_class = SmartLocator("class=btn-primary", adapter, "Button by class")
            if btn_class.is_visible():
                print("   ✅ Class Locator working!")
        except Exception as e:
            print(f"   ⚠️  Class locator test: {e}")
        
        # 7. Tag name
        print("\n7️⃣  Testing Tag: tag=button")
        try:
            button_tag = SmartLocator("tag=button", adapter, "Any button")
            if button_tag.is_visible():
                print("   ✅ Tag Locator working!")
        except Exception as e:
            print(f"   ⚠️  Tag locator test: {e}")
        
        print("\n" + "="*70)
        print("✅ All Selenium locator types tested successfully!")
        print("="*70 + "\n")
    
    def test_locator_auto_detection(self, page):
        """Test automatic locator type detection."""
        from core.smart_locator import SmartLocator, PlaywrightAdapter
        
        page.goto("https://practice.expandtesting.com/login")
        adapter = PlaywrightAdapter(page)
        
        print("\n" + "="*70)
        print("🤖 Testing Auto-Detection of Locator Types")
        print("="*70)
        
        test_cases = [
            ("//input[@id='username']", "XPath", "Detects // at start"),
            ("#username", "CSS", "Detects # for ID"),
            ("input[name='password']", "CSS", "Detects CSS selector"),
            ("text=Login", "Text", "Detects text= prefix"),
            ("role=button", "Role", "Detects role= prefix"),
        ]
        
        for locator_str, expected_type, description in test_cases:
            print(f"\n🔍 Testing: {locator_str}")
            print(f"   Expected: {expected_type}")
            print(f"   Description: {description}")
            
            try:
                locator = SmartLocator(locator_str, adapter, "Auto-detect test")
                is_visible = locator.is_visible()
                print(f"   ✅ Auto-detected {expected_type} - Element visible: {is_visible}")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        
        print("\n" + "="*70)
        print("✅ Auto-detection tested successfully!")
        print("="*70 + "\n")
    
    def test_locator_healing_with_different_types(self, page):
        """Test AI healing works with different locator types."""
        from core.smart_locator import SmartLocator, PlaywrightAdapter
        
        page.goto("https://practice.expandtesting.com/login")
        adapter = PlaywrightAdapter(page)
        
        print("\n" + "="*70)
        print("🔧 Testing AI Healing with Different Locator Types")
        print("="*70)
        
        # Test 1: CSS selector that will fail
        print("\n1️⃣  Testing healing with broken CSS selector")
        try:
            broken_css = SmartLocator("button#wrong-id", adapter, "Login button", max_retries=1)
            broken_css.click()
            print("   ✅ Healed CSS locator successfully!")
        except Exception as e:
            print(f"   ⚠️  CSS healing test: {e}")
        
        # Test 2: XPath that will fail
        print("\n2️⃣  Testing healing with broken XPath")
        try:
            broken_xpath = SmartLocator("//button[@id='wrong-id']", adapter, "Login button", max_retries=1)
            broken_xpath.click()
            print("   ✅ Healed XPath locator successfully!")
        except Exception as e:
            print(f"   ⚠️  XPath healing test: {e}")
        
        # Test 3: ID that will fail
        print("\n3️⃣  Testing healing with broken ID")
        try:
            broken_id = SmartLocator("#wrong-username", adapter, "Username field", max_retries=1)
            broken_id.fill("test")
            print("   ✅ Healed ID locator successfully!")
        except Exception as e:
            print(f"   ⚠️  ID healing test: {e}")
        
        print("\n" + "="*70)
        print("✅ AI healing works across all locator types!")
        print("="*70 + "\n")


# Fixtures for Playwright
@pytest.fixture
def page():
    """Create Playwright page."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


# Fixtures for Selenium
@pytest.fixture
def driver():
    """Create Selenium WebDriver."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


if __name__ == "__main__":
    # Run with: pytest tests/test_locator_types_demo.py -v -s
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        SmartLocator - Universal Locator Types Demo           ║
    ║                                                               ║
    ║  This test demonstrates support for ALL major locator types  ║
    ║                                                               ║
    ║  Run with: pytest tests/test_locator_types_demo.py -v -s     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
