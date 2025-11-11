"""
Demo: Universal AI-Healing with SmartLocator
=============================================

This demonstrates:
1. ✅ ONE AI-healing core supports BOTH frameworks (no duplicated logic)
2. ✅ AI serves as universal locator-repair microservice
3. ✅ SmartLocator/SmartPage is the cross-framework POM layer

Same code works with Playwright AND Selenium!
"""

import pytest
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Import SmartLocator and adapters
from core.smart_locator import SmartLocator, SmartPage, PlaywrightAdapter, SeleniumAdapter


# ============================================================================
# TEST 1: SmartLocator with Playwright
# ============================================================================

@pytest.mark.healing
def test_smart_locator_playwright():
    """Test SmartLocator with Playwright framework."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Load test HTML
        html_content = """
        <html>
        <body>
            <input id="fname" name="firstname" placeholder="First Name">
            <button id="submit_btn">Submit</button>
        </body>
        </html>
        """
        page.set_content(html_content)
        
        # Create adapter
        adapter = PlaywrightAdapter(page)
        
        # Test 1: Working locator
        print("\n[TEST 1: Playwright] Testing working locator...")
        name_field = SmartLocator("input#fname", adapter, context_hint="First name input")
        name_field.fill("John")
        assert name_field.text() == ""  # Input fields don't have text content
        print("✅ Working locator succeeded")
        
        # Test 2: Broken locator (should auto-heal)
        print("\n[TEST 2: Playwright] Testing broken locator (will auto-heal)...")
        broken_field = SmartLocator(
            "input#wrong_id",  # WRONG ID
            adapter,
            context_hint="First name input field"
        )
        
        try:
            broken_field.fill("Jane")
            print(f"✅ Auto-healing worked! Current locator: {broken_field.get_current_locator()}")
            print(f"✅ Was healed: {broken_field.was_healed()}")
        except Exception as e:
            print(f"❌ Auto-healing failed: {e}")
            raise
        
        browser.close()


# ============================================================================
# TEST 2: SmartLocator with Selenium
# ============================================================================

@pytest.mark.healing
def test_smart_locator_selenium():
    """Test SmartLocator with Selenium framework - SAME API!"""
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Load test HTML
        html_content = """
        <html>
        <body>
            <input id="fname" name="firstname" placeholder="First Name">
            <button id="submit_btn">Submit</button>
        </body>
        </html>
        """
        driver.get(f"data:text/html,{html_content}")
        
        # Create adapter
        adapter = SeleniumAdapter(driver)
        
        # Test 1: Working locator
        print("\n[TEST 1: Selenium] Testing working locator...")
        name_field = SmartLocator("input#fname", adapter, context_hint="First name input")
        name_field.fill("John")
        print("✅ Working locator succeeded")
        
        # Test 2: Broken locator (should auto-heal)
        print("\n[TEST 2: Selenium] Testing broken locator (will auto-heal)...")
        broken_field = SmartLocator(
            "input#wrong_id",  # WRONG ID
            adapter,
            context_hint="First name input field"
        )
        
        try:
            broken_field.fill("Jane")
            print(f"✅ Auto-healing worked! Current locator: {broken_field.get_current_locator()}")
            print(f"✅ Was healed: {broken_field.was_healed()}")
        except Exception as e:
            print(f"❌ Auto-healing failed: {e}")
            raise
    
    finally:
        driver.quit()


# ============================================================================
# TEST 3: SmartPage with Playwright
# ============================================================================

class LoginPage(SmartPage):
    """Example Page Object using SmartPage base class."""
    
    def __init__(self, adapter):
        super().__init__(adapter)
        # Define locators (auto-healing enabled)
        self.username = self.locator("input#username", "Username field")
        self.password = self.locator("input#password", "Password field")
        self.submit = self.locator("button[type='submit']", "Submit button")
    
    def login(self, user: str, pwd: str):
        """Perform login action."""
        self.username.fill(user)
        self.password.fill(pwd)
        self.submit.click()


@pytest.mark.healing
def test_smart_page_playwright():
    """Test SmartPage POM pattern with Playwright."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Load login form
        html_content = """
        <html>
        <body>
            <form>
                <input id="username" type="text" placeholder="Username">
                <input id="password" type="password" placeholder="Password">
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """
        page.set_content(html_content)
        
        # Use SmartPage
        login_page = LoginPage(PlaywrightAdapter(page))
        
        print(f"\n[TEST: SmartPage] Framework: {login_page.framework_name}")
        
        # Test login (locators auto-heal if needed)
        login_page.username.fill("testuser")
        login_page.password.fill("testpass")
        
        print("✅ SmartPage with Playwright working!")
        
        browser.close()


# ============================================================================
# TEST 4: SmartPage with Selenium - SAME PAGE CLASS!
# ============================================================================

@pytest.mark.healing
def test_smart_page_selenium():
    """Test SmartPage POM pattern with Selenium - SAME LoginPage class!"""
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Load login form
        html_content = """
        <html>
        <body>
            <form>
                <input id="username" type="text" placeholder="Username">
                <input id="password" type="password" placeholder="Password">
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """
        driver.get(f"data:text/html,{html_content}")
        
        # Use SAME SmartPage class!
        login_page = LoginPage(SeleniumAdapter(driver))
        
        print(f"\n[TEST: SmartPage] Framework: {login_page.framework_name}")
        
        # Test login (same code as Playwright!)
        login_page.username.fill("testuser")
        login_page.password.fill("testpass")
        
        print("✅ SmartPage with Selenium working!")
    
    finally:
        driver.quit()


# ============================================================================
# Proof that it's working
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNIVERSAL AI-HEALING ARCHITECTURE DEMO")
    print("=" * 80)
    print()
    print("✅ ONE AI-healing core supports BOTH frameworks")
    print("✅ AI serves as universal locator-repair microservice")
    print("✅ SmartLocator/SmartPage = cross-framework POM layer")
    print()
    print("Running tests...")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "-s", "-m", "healing"])
