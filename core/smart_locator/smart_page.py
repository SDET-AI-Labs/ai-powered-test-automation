"""
SmartPage - Cross-Framework Page Object Model Base Class
=========================================================

Base class for Page Object Model that works with any framework.

Example:
    # Playwright
    class LoginPage(SmartPage):
        def __init__(self, page):
            super().__init__(PlaywrightAdapter(page))
            self.username = self.locator("input#username", "Username field")
            self.password = self.locator("input#password", "Password field")
            self.submit = self.locator("button[type='submit']", "Submit button")
        
        def login(self, user, pwd):
            self.username.fill(user)
            self.password.fill(pwd)
            self.submit.click()
    
    # Selenium - SAME PAGE CLASS!
    class LoginPage(SmartPage):
        def __init__(self, driver):
            super().__init__(SeleniumAdapter(driver))
            # Same code as above!
"""

from typing import Dict
from .smart_locator import SmartLocator
from .framework_adapter import FrameworkAdapter


class SmartPage:
    """
    Base class for Page Object Model with cross-framework support.
    
    Features:
    - Works with Playwright, Selenium, or any framework
    - Auto-healing locators
    - Clean, framework-agnostic API
    """
    
    def __init__(self, adapter: FrameworkAdapter):
        """
        Initialize page with framework adapter.
        
        Args:
            adapter: PlaywrightAdapter, SeleniumAdapter, or custom adapter
        """
        self.adapter = adapter
        self._locators: Dict[str, SmartLocator] = {}
    
    def locator(
        self,
        selector: str,
        context_hint: str = "",
        max_retries: int = 1
    ) -> SmartLocator:
        """
        Create a self-healing locator.
        
        Args:
            selector: CSS selector, XPath, etc.
            context_hint: Description for AI (e.g., "Login button")
            max_retries: How many heal attempts (default: 1)
            
        Returns:
            SmartLocator instance
        """
        # Cache locators by selector
        cache_key = f"{selector}:{context_hint}"
        
        if cache_key not in self._locators:
            self._locators[cache_key] = SmartLocator(
                locator=selector,
                adapter=self.adapter,
                context_hint=context_hint,
                max_retries=max_retries
            )
        
        return self._locators[cache_key]
    
    def get_page_source(self) -> str:
        """Get current page HTML."""
        return self.adapter.get_page_source()
    
    def click(self, selector: str, context_hint: str = ""):
        """Quick click without creating locator variable."""
        self.locator(selector, context_hint).click()
    
    def fill(self, selector: str, text: str, context_hint: str = ""):
        """Quick fill without creating locator variable."""
        self.locator(selector, context_hint).fill(text)
    
    def text(self, selector: str, context_hint: str = "") -> str:
        """Quick get text without creating locator variable."""
        return self.locator(selector, context_hint).text()
    
    def is_visible(self, selector: str, context_hint: str = "") -> bool:
        """Quick visibility check without creating locator variable."""
        return self.locator(selector, context_hint).is_visible()
    
    @property
    def framework_name(self) -> str:
        """Get the framework being used."""
        return self.adapter.framework_name
