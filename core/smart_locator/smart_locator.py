"""
SmartLocator - Self-Healing Locator Wrapper with Universal Locator Support
===========================================================================

Wraps a locator string with AI-powered auto-healing capabilities.
Supports ALL major locator types for both Playwright and Selenium.

Supported Locator Types:
------------------------

PLAYWRIGHT:
- CSS Selector: "button#submit", ".btn-primary", "input[name='username']"
- XPath: "//button[@id='submit']", "xpath=//button"
- Text: "text=Click Here", "text='Exact match'"
- Role: "role=button[name='Submit']"
- Test ID: "[data-testid=login-btn]", "data-testid=login-btn"
- Label: "label=Username"
- Placeholder: "placeholder=Enter name"
- Alt Text: "alt=Logo"
- Title: "title=Submit form"

SELENIUM:
- CSS Selector: "button#submit", ".btn-primary" (default)
- XPath: "//button[@id='submit']", "xpath=//button"
- ID: "id=submit", "#submit"
- Name: "name=username"
- Class: "class=btn-primary", ".btn-primary"
- Tag: "tag=button"
- Link Text: "link=Click Here"
- Partial Link: "partial_link=Click"

Example:
    # Playwright
    locator = SmartLocator("button#submit", adapter=PlaywrightAdapter(page))
    locator = SmartLocator("text=Submit", adapter=PlaywrightAdapter(page))
    locator = SmartLocator("role=button[name='Submit']", adapter=PlaywrightAdapter(page))
    locator.click()  # Auto-heals if locator breaks
    
    # Selenium
    locator = SmartLocator("id=submit", adapter=SeleniumAdapter(driver))
    locator = SmartLocator("xpath=//button[@id='submit']", adapter=SeleniumAdapter(driver))
    locator = SmartLocator("link=Click Here", adapter=SeleniumAdapter(driver))
    locator.click()  # Same API, different framework!
"""

from typing import Optional
import sys
from pathlib import Path

# Import locator repair service
from services.locator_repair import LocatorRepairService

from .framework_adapter import FrameworkAdapter


class SmartLocator:
    """
    Self-healing locator that automatically repairs broken selectors.
    
    Works with any framework through adapters.
    """
    
    def __init__(
        self,
        locator: str,
        adapter: FrameworkAdapter,
        context_hint: str = "",
        max_retries: int = 1
    ):
        """
        Initialize SmartLocator.
        
        Args:
            locator: The selector string (CSS, XPath, etc.)
            adapter: Framework adapter (PlaywrightAdapter, SeleniumAdapter)
            context_hint: Human-readable description (e.g., "Submit button")
            max_retries: How many times to attempt healing (default: 1)
        """
        self.original_locator = locator
        self.current_locator = locator
        self.adapter = adapter
        self.context_hint = context_hint
        self.max_retries = max_retries
        self.repair_service = LocatorRepairService()
        self.healed = False
    
    def click(self):
        """Click the element (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.click(loc)
        )
    
    def fill(self, text: str):
        """Fill text into element (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.fill(loc, text)
        )
    
    def text(self) -> str:
        """Get element text (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_text(loc)
        )
    
    def is_visible(self) -> bool:
        """Check if element is visible (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.is_visible(loc)
        )
    
    def element(self):
        """Get the underlying framework element."""
        return self._execute_with_healing(
            lambda loc: self.adapter.find_element(loc)
        )
    
    def _execute_with_healing(self, action):
        """
        Execute action with automatic healing on failure.
        
        Args:
            action: Lambda that takes locator and performs action
            
        Returns:
            Result of action
        """
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # Try with current locator
                result = action(self.current_locator)
                
                # Log if we successfully healed
                if self.healed:
                    print(f"✅ Healed locator working: {self.current_locator}")
                
                return result
                
            except Exception as e:
                last_error = e
                
                if retries >= self.max_retries:
                    print(f"❌ Max retries reached. Last error: {e}")
                    raise
                
                # Attempt healing
                print(f"⚠️  Locator failed: {self.current_locator}")
                print(f"🔧 Attempting AI-powered repair... (attempt {retries + 1}/{self.max_retries + 1})")
                
                repaired = self._heal_locator()
                
                if repaired:
                    self.current_locator = repaired
                    self.healed = True
                    retries += 1
                else:
                    print(f"❌ Healing failed. Original error: {e}")
                    raise
        
        raise last_error or Exception("Unknown error in healing process")
    
    def _heal_locator(self) -> Optional[str]:
        """
        Attempt to heal the broken locator using AI service.
        
        Returns:
            Repaired locator or None if healing failed
        """
        try:
            # Get current page HTML
            page_source = self.adapter.get_page_source()
            
            # Call universal repair service
            framework_name = self.adapter.framework_name
            if framework_name not in ("playwright", "selenium"):
                framework_name = "playwright"  # Default fallback
                
            response = self.repair_service.repair_locator(
                framework=framework_name,  # type: ignore
                page_source=page_source,
                failed_locator=self.current_locator,
                context_hint=self.context_hint
            )
            
            if response.success and response.repaired_locator:
                print(f"✅ AI suggested: {response.repaired_locator}")
                return response.repaired_locator
            else:
                print(f"❌ AI healing failed: {response.error}")
                return None
                
        except Exception as e:
            print(f"❌ Healing service error: {e}")
            return None
    
    def get_current_locator(self) -> str:
        """Get the current working locator (may be healed)."""
        return self.current_locator
    
    def was_healed(self) -> bool:
        """Check if locator was healed."""
        return self.healed
    
    def reset(self):
        """Reset to original locator."""
        self.current_locator = self.original_locator
        self.healed = False
    
    # ==================== FORM CONTROLS (with auto-healing) ====================
    
    def check(self):
        """Check checkbox (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.check_checkbox(loc)
        )
    
    def uncheck(self):
        """Uncheck checkbox (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.uncheck_checkbox(loc)
        )
    
    def is_checked(self) -> bool:
        """Check if checkbox/radio is checked (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.is_checked(loc)
        )
    
    def select_option(self, value: str, by: str = "value"):
        """
        Select dropdown option (with auto-healing).
        
        Args:
            value: Value to select
            by: Selection method - "value", "label"/"text", or "index"
        """
        return self._execute_with_healing(
            lambda loc: self.adapter.select_dropdown(loc, value, by)
        )
    
    def get_selected_option(self) -> str:
        """Get selected dropdown option (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_selected_option(loc)
        )
    
    def upload_file(self, file_path: str):
        """Upload file (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.upload_file(loc, file_path)
        )
    
    # ==================== HOVER & VISIBILITY (with auto-healing) ====================
    
    def hover(self):
        """Hover over element for tooltips/dropdowns (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.hover(loc)
        )
    
    def wait_visible(self, timeout: int = 10) -> bool:
        """Wait for element to be visible (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.wait_for_visible(loc, timeout)
        )
    
    def wait_hidden(self, timeout: int = 10) -> bool:
        """Wait for element to be hidden (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.wait_for_hidden(loc, timeout)
        )
    
    def is_enabled(self) -> bool:
        """Check if element is enabled (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.is_enabled(loc)
        )
    
    # ==================== ATTRIBUTES & PROPERTIES (with auto-healing) ====================
    
    def get_attribute(self, attribute: str) -> Optional[str]:
        """Get element attribute (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_attribute(loc, attribute)
        )
    
    def get_property(self, property_name: str):
        """Get element property (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_property(loc, property_name)
        )
    
    def get_value(self) -> str:
        """Get input/textarea value (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_value(loc)
        )
    
    # ==================== ACTIONS (with auto-healing) ====================
    
    def double_click(self):
        """Double-click element (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.double_click(loc)
        )
    
    def right_click(self):
        """Right-click element for context menu (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.right_click(loc)
        )
    
    def drag_to(self, target_locator: str):
        """Drag this element to target (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.drag_and_drop(loc, target_locator)
        )
    
    def scroll_into_view(self):
        """Scroll element into view (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.scroll_into_view(loc)
        )
    
    def press_key(self, key: str):
        """Press keyboard key on element (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.press_key(loc, key)
        )
    
    # ==================== MULTI-ELEMENT (with auto-healing) ====================
    
    def count(self) -> int:
        """Get count of matching elements (with auto-healing)."""
        return self._execute_with_healing(
            lambda loc: self.adapter.get_element_count(loc)
        )
