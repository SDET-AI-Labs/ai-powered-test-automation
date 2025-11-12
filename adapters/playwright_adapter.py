"""
Playwright Stealth Adapter
===========================

Launch Playwright browsers with anti-detection measures to bypass
automation detection on protected sites.

Features:
- Disable automation control flags
- Override navigator.webdriver property
- Spoof chrome runtime objects
- Set realistic user agents and languages
- Optional proxy support

Author: Ram
Date: November 12, 2025
Phase: 7 - Universal Interactor
"""

from typing import Optional, Dict, Any
import logging
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

log = logging.getLogger(__name__)


def launch_stealth_browser(
    headless: bool = True,
    proxy: Optional[str] = None,
    user_agent: Optional[str] = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    playwright_instance: Optional[Any] = None,
) -> tuple[Browser, BrowserContext, Page]:
    """
    Launch a Playwright browser with stealth measures to bypass bot detection.
    
    Anti-detection measures applied:
    1. --disable-blink-features=AutomationControlled (disable automation flags)
    2. navigator.webdriver = undefined (hide automation property)
    3. navigator.plugins with realistic length
    4. navigator.languages spoofing
    5. chrome runtime object for compatibility
    
    Args:
        headless: Run in headless mode (default: True)
        proxy: Proxy URL in format "http://host:port" (optional)
        user_agent: Custom user agent string (optional, uses default Chrome UA if None)
        viewport_width: Browser viewport width (default: 1920)
        viewport_height: Browser viewport height (default: 1080)
        playwright_instance: Existing Playwright instance (optional, creates new if None)
        
    Returns:
        tuple: (browser, context, page) - All Playwright objects
        
    Example:
        >>> browser, context, page = launch_stealth_browser(headless=False)
        >>> page.goto("https://www.cargain.com/login")
        >>> # ... perform actions ...
        >>> browser.close()
        
    Example with proxy:
        >>> proxy_url = "http://proxy.example.com:8080"
        >>> browser, context, page = launch_stealth_browser(proxy=proxy_url)
    """
    log.info(f"[StealthAdapter] Launching browser headless={headless} proxy={proxy is not None}")
    
    # Use provided playwright instance or create new one
    if playwright_instance is None:
        playwright = sync_playwright().start()
    else:
        playwright = playwright_instance
    
    # Build launch arguments for anti-detection
    launch_args = [
        "--disable-blink-features=AutomationControlled",  # Most important: disable automation detection
        "--disable-features=IsolateOrigins,site-per-process",  # Reduce site isolation overhead
        "--disable-web-security",  # Allow cross-origin (use carefully)
        "--disable-features=VizDisplayCompositor",  # Performance optimization
    ]
    
    # Build browser launch options
    browser_options: Dict[str, Any] = {
        "headless": headless,
        "args": launch_args,
    }
    
    # Add proxy if provided
    if proxy:
        log.info(f"[StealthAdapter] Configuring proxy: {proxy}")
        browser_options["proxy"] = {"server": proxy}
    
    # Launch browser
    browser = playwright.chromium.launch(**browser_options)
    
    # Create context with stealth options
    context_options: Dict[str, Any] = {
        "viewport": {"width": viewport_width, "height": viewport_height},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "permissions": ["geolocation"],
    }
    
    # Set user agent if provided
    if user_agent:
        context_options["user_agent"] = user_agent
    else:
        # Use realistic Chrome user agent
        context_options["user_agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    context = browser.new_context(**context_options)
    
    # Apply JavaScript overrides for anti-detection
    # This is the critical part that hides automation markers
    context.add_init_script("""
        // Override navigator.webdriver (primary detection method)
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Override navigator.plugins to appear as real browser
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],  // Non-zero length = real browser
        });
        
        // Override navigator.languages for realism
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Add chrome runtime object (appears in real Chrome)
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {},
        };
        
        // Override permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Add realistic battery API
        Object.defineProperty(navigator, 'getBattery', {
            value: () => Promise.resolve({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1.0,
            }),
        });
        
        // Console override to hide automation markers
        console.debug('[StealthAdapter] Anti-detection scripts loaded');
    """)
    
    # Create a new page
    page = context.new_page()
    
    log.info(f"[StealthAdapter] ✅ Browser launched successfully")
    log.info(f"[StealthAdapter] User-Agent: {context_options['user_agent'][:50]}...")
    
    return browser, context, page


def launch_stealth_browser_simple(headless: bool = True) -> Page:
    """
    Simplified stealth browser launch that returns only the page.
    
    Note: Browser and context are not closed automatically.
    Use this for quick tests only. For production, use launch_stealth_browser().
    
    Args:
        headless: Run in headless mode (default: True)
        
    Returns:
        Page: Playwright page object
        
    Example:
        >>> page = launch_stealth_browser_simple()
        >>> page.goto("https://example.com")
    """
    _, _, page = launch_stealth_browser(headless=headless)
    return page


def get_stealth_context_options() -> Dict[str, Any]:
    """
    Get recommended context options for stealth browsing.
    
    Returns:
        dict: Context options for browser.new_context()
        
    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> playwright = sync_playwright().start()
        >>> browser = playwright.chromium.launch()
        >>> options = get_stealth_context_options()
        >>> context = browser.new_context(**options)
    """
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "permissions": ["geolocation"],
    }


def get_stealth_launch_args() -> list[str]:
    """
    Get recommended browser launch arguments for stealth.
    
    Returns:
        list: Launch arguments for browser.launch(args=...)
        
    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> playwright = sync_playwright().start()
        >>> args = get_stealth_launch_args()
        >>> browser = playwright.chromium.launch(args=args)
    """
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
    ]


def apply_stealth_scripts(context: BrowserContext):
    """
    Apply anti-detection scripts to an existing browser context.
    
    Args:
        context: Playwright BrowserContext to apply scripts to
        
    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> playwright = sync_playwright().start()
        >>> browser = playwright.chromium.launch()
        >>> context = browser.new_context()
        >>> apply_stealth_scripts(context)
    """
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {},
        };
        
        console.debug('[StealthAdapter] Anti-detection scripts applied');
    """)
    
    log.info("[StealthAdapter] Anti-detection scripts applied to context")


# Example usage and testing
if __name__ == "__main__":
    # Test basic stealth launch
    print("Testing stealth browser launch...")
    
    browser, context, page = launch_stealth_browser(headless=False)
    
    # Test on a known bot-detection site
    page.goto("https://bot.sannysoft.com/")
    page.wait_for_timeout(3000)
    
    # Check if webdriver is detected
    is_webdriver = page.evaluate("() => navigator.webdriver")
    print(f"navigator.webdriver detected: {is_webdriver}")
    
    # Keep browser open for manual inspection
    input("Press Enter to close browser...")
    
    browser.close()
    print("✅ Stealth browser test complete")
