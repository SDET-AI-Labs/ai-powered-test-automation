"""
Framework Adapters
==================

Adapters to make different web automation frameworks work with SmartLocator.

This allows the same SmartLocator/SmartPage API to work with:
- Playwright
- Selenium  
- Future frameworks (Puppeteer, Cypress, etc.)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class FrameworkAdapter(ABC):
    """Base adapter interface for web automation frameworks."""
    
    @abstractmethod
    def get_page_source(self) -> str:
        """Get current page HTML."""
        pass
    
    @abstractmethod
    def find_element(self, locator: str) -> Any:
        """Find element using locator."""
        pass
    
    @abstractmethod
    def click(self, locator: str):
        """Click element."""
        pass
    
    @abstractmethod
    def fill(self, locator: str, text: str):
        """Fill text into element."""
        pass
    
    @abstractmethod
    def get_text(self, locator: str) -> str:
        """Get element text."""
        pass
    
    @abstractmethod
    def is_visible(self, locator: str) -> bool:
        """Check if element is visible."""
        pass
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Return framework name (playwright, selenium, etc.)."""
        pass


class PlaywrightAdapter(FrameworkAdapter):
    """Adapter for Playwright framework."""
    
    def __init__(self, page):
        """
        Initialize with Playwright Page object.
        
        Args:
            page: playwright.sync_api.Page instance
        """
        self.page = page
    
    def get_page_source(self) -> str:
        return self.page.content()
    
    def find_element(self, locator: str):
        return self.page.locator(locator)
    
    def click(self, locator: str):
        self.page.locator(locator).click()
    
    def fill(self, locator: str, text: str):
        self.page.locator(locator).fill(text)
    
    def get_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content() or ""
    
    def is_visible(self, locator: str) -> bool:
        try:
            return self.page.locator(locator).is_visible()
        except:
            return False
    
    @property
    def framework_name(self) -> str:
        return "playwright"


class SeleniumAdapter(FrameworkAdapter):
    """Adapter for Selenium framework."""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.
        
        Args:
            driver: selenium.webdriver instance (Chrome, Firefox, etc.)
        """
        self.driver = driver
    
    def get_page_source(self) -> str:
        return self.driver.page_source
    
    def find_element(self, locator: str):
        """
        Find element using locator.
        Supports: CSS selector, XPath, ID, etc.
        """
        from selenium.webdriver.common.by import By
        
        # Detect locator type
        if locator.startswith("//") or locator.startswith("(//"):
            return self.driver.find_element(By.XPATH, locator)
        elif locator.startswith("#"):
            return self.driver.find_element(By.CSS_SELECTOR, locator)
        else:
            # Default to CSS selector
            return self.driver.find_element(By.CSS_SELECTOR, locator)
    
    def click(self, locator: str):
        element = self.find_element(locator)
        element.click()
    
    def fill(self, locator: str, text: str):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator: str) -> str:
        element = self.find_element(locator)
        return element.text
    
    def is_visible(self, locator: str) -> bool:
        try:
            element = self.find_element(locator)
            return element.is_displayed()
        except:
            return False
    
    @property
    def framework_name(self) -> str:
        return "selenium"
