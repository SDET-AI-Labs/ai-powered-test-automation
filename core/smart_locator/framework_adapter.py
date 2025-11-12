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
from typing import Any, Optional, List, Dict
import time


class FrameworkAdapter(ABC):
    """
    Base adapter interface for web automation frameworks.
    
    Supports ALL UI element types:
    - Form controls (inputs, checkboxes, radios, selects, textareas)
    - Buttons and navigation (buttons, links, tabs, menus)
    - Containers (modals, dialogs, cards, panels)
    - Data displays (tables, trees, charts)
    - Dynamic UI (autocomplete, dropdowns, carousels, tooltips)
    - Accessibility (ARIA roles and semantic elements)
    """
    
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
    
    # ==================== FORM CONTROLS ====================
    
    @abstractmethod
    def check_checkbox(self, locator: str):
        """Check a checkbox."""
        pass
    
    @abstractmethod
    def uncheck_checkbox(self, locator: str):
        """Uncheck a checkbox."""
        pass
    
    @abstractmethod
    def is_checked(self, locator: str) -> bool:
        """Check if checkbox/radio is checked."""
        pass
    
    @abstractmethod
    def select_radio(self, locator: str):
        """Select a radio button."""
        pass
    
    @abstractmethod
    def select_dropdown(self, locator: str, value: str, by: str = "value"):
        """Select dropdown option by value, text, or index."""
        pass
    
    @abstractmethod
    def get_selected_option(self, locator: str) -> str:
        """Get selected dropdown option text."""
        pass
    
    @abstractmethod
    def upload_file(self, locator: str, file_path: str):
        """Upload file to file input."""
        pass
    
    # ==================== HOVER & VISIBILITY ====================
    
    @abstractmethod
    def hover(self, locator: str):
        """Hover over element (for tooltips, dropdowns)."""
        pass
    
    @abstractmethod
    def wait_for_visible(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be visible."""
        pass
    
    @abstractmethod
    def wait_for_hidden(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be hidden."""
        pass
    
    @abstractmethod
    def is_enabled(self, locator: str) -> bool:
        """Check if element is enabled."""
        pass
    
    # ==================== ATTRIBUTES & PROPERTIES ====================
    
    @abstractmethod
    def get_attribute(self, locator: str, attribute: str) -> Optional[str]:
        """Get element attribute value."""
        pass
    
    @abstractmethod
    def get_property(self, locator: str, property_name: str) -> Any:
        """Get element property value."""
        pass
    
    @abstractmethod
    def get_value(self, locator: str) -> str:
        """Get input/textarea value."""
        pass
    
    # ==================== ACTIONS ====================
    
    @abstractmethod
    def double_click(self, locator: str):
        """Double-click element."""
        pass
    
    @abstractmethod
    def right_click(self, locator: str):
        """Right-click element (context menu)."""
        pass
    
    @abstractmethod
    def drag_and_drop(self, source_locator: str, target_locator: str):
        """Drag and drop from source to target."""
        pass
    
    @abstractmethod
    def scroll_into_view(self, locator: str):
        """Scroll element into view."""
        pass
    
    @abstractmethod
    def press_key(self, locator: str, key: str):
        """Press keyboard key on element."""
        pass
    
    # ==================== CONTAINERS & MODALS ====================
    
    @abstractmethod
    def is_modal_open(self, locator: str = "role=dialog") -> bool:
        """Check if modal/dialog is open."""
        pass
    
    @abstractmethod
    def close_modal(self, locator: str = "role=dialog"):
        """Close modal/dialog."""
        pass
    
    # ==================== TABLES ====================
    
    @abstractmethod
    def get_table_data(self, locator: str) -> List[List[str]]:
        """Get all table data as 2D array."""
        pass
    
    @abstractmethod
    def get_table_row(self, table_locator: str, row_index: int) -> List[str]:
        """Get specific table row data."""
        pass
    
    @abstractmethod
    def get_table_cell(self, table_locator: str, row: int, col: int) -> str:
        """Get specific table cell text."""
        pass
    
    # ==================== MULTI-ELEMENT ====================
    
    @abstractmethod
    def find_elements(self, locator: str) -> List[Any]:
        """Find multiple elements."""
        pass
    
    @abstractmethod
    def get_element_count(self, locator: str) -> int:
        """Get count of matching elements."""
        pass
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Return framework name (playwright, selenium, etc.)."""
        pass


class PlaywrightAdapter(FrameworkAdapter):
    """
    Adapter for Playwright framework with support for ALL UI element types.
    
    Supports:
    - All standard locators (CSS, XPath, Text, Role, etc.)
    - Form controls (inputs, checkboxes, radios, selects, file uploads)
    - Hover interactions (tooltips, dropdowns, popovers)
    - Dynamic elements (autocomplete, modals, tables)
    - ARIA roles and accessibility
    """
    
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
        """
        Find element using ANY Playwright locator type.
        
        Supported locator types:
        - CSS: button#submit (default)
        - XPath: //button[@id='submit'] or xpath=//button
        - Text: text=Click Here or text="Exact match"
        - Role: role=button[name="Submit"]
        - Test ID: data-testid=submit or [data-testid=submit]
        - Label: label=Username
        - Placeholder: placeholder=Enter name
        - Alt Text: alt=Logo
        - Title: title=Submit form
        
        Examples:
            "button#submit"                    # CSS
            "text=Click Here"                  # Visible text
            "role=button[name='Submit']"       # ARIA role
            "[data-testid=login-btn]"          # Test ID
            "xpath=//button[@id='submit']"     # XPath
        """
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
    
    # ==================== FORM CONTROLS ====================
    
    def check_checkbox(self, locator: str):
        """Check a checkbox."""
        self.page.locator(locator).check()
    
    def uncheck_checkbox(self, locator: str):
        """Uncheck a checkbox."""
        self.page.locator(locator).uncheck()
    
    def is_checked(self, locator: str) -> bool:
        """Check if checkbox/radio is checked."""
        return self.page.locator(locator).is_checked()
    
    def select_radio(self, locator: str):
        """Select a radio button."""
        self.page.locator(locator).check()
    
    def select_dropdown(self, locator: str, value: str, by: str = "value"):
        """
        Select dropdown option.
        
        Args:
            locator: Dropdown locator
            value: Value to select
            by: Selection method - "value", "label", or "index"
        """
        if by == "value":
            self.page.locator(locator).select_option(value=value)
        elif by == "label":
            self.page.locator(locator).select_option(label=value)
        elif by == "index":
            self.page.locator(locator).select_option(index=int(value))
    
    def get_selected_option(self, locator: str) -> str:
        """Get selected dropdown option text."""
        return self.page.locator(locator).input_value()
    
    def upload_file(self, locator: str, file_path: str):
        """Upload file to file input."""
        self.page.locator(locator).set_input_files(file_path)
    
    # ==================== HOVER & VISIBILITY ====================
    
    def hover(self, locator: str):
        """Hover over element (for tooltips, dropdowns)."""
        self.page.locator(locator).hover()
    
    def wait_for_visible(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be visible."""
        try:
            self.page.locator(locator).wait_for(state="visible", timeout=timeout * 1000)
            return True
        except:
            return False
    
    def wait_for_hidden(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be hidden."""
        try:
            self.page.locator(locator).wait_for(state="hidden", timeout=timeout * 1000)
            return True
        except:
            return False
    
    def is_enabled(self, locator: str) -> bool:
        """Check if element is enabled."""
        return self.page.locator(locator).is_enabled()
    
    # ==================== ATTRIBUTES & PROPERTIES ====================
    
    def get_attribute(self, locator: str, attribute: str) -> Optional[str]:
        """Get element attribute value."""
        return self.page.locator(locator).get_attribute(attribute)
    
    def get_property(self, locator: str, property_name: str) -> Any:
        """Get element property value."""
        return self.page.locator(locator).evaluate(f"el => el.{property_name}")
    
    def get_value(self, locator: str) -> str:
        """Get input/textarea value."""
        return self.page.locator(locator).input_value()
    
    # ==================== ACTIONS ====================
    
    def double_click(self, locator: str):
        """Double-click element."""
        self.page.locator(locator).dblclick()
    
    def right_click(self, locator: str):
        """Right-click element (context menu)."""
        self.page.locator(locator).click(button="right")
    
    def drag_and_drop(self, source_locator: str, target_locator: str):
        """Drag and drop from source to target."""
        self.page.locator(source_locator).drag_to(self.page.locator(target_locator))
    
    def scroll_into_view(self, locator: str):
        """Scroll element into view."""
        self.page.locator(locator).scroll_into_view_if_needed()
    
    def press_key(self, locator: str, key: str):
        """Press keyboard key on element."""
        self.page.locator(locator).press(key)
    
    # ==================== CONTAINERS & MODALS ====================
    
    def is_modal_open(self, locator: str = "role=dialog") -> bool:
        """Check if modal/dialog is open."""
        return self.is_visible(locator)
    
    def close_modal(self, locator: str = "role=dialog"):
        """Close modal/dialog (try Escape key or close button)."""
        try:
            # Try pressing Escape
            self.page.keyboard.press("Escape")
        except:
            # Try finding and clicking close button
            try:
                close_btn = f"{locator} >> button[aria-label='Close']"
                if self.is_visible(close_btn):
                    self.click(close_btn)
            except:
                pass
    
    # ==================== TABLES ====================
    
    def get_table_data(self, locator: str) -> List[List[str]]:
        """Get all table data as 2D array."""
        rows = self.page.locator(f"{locator} >> tr").all()
        data = []
        for row in rows:
            cells = row.locator("td, th").all()
            row_data = [cell.text_content() or "" for cell in cells]
            data.append(row_data)
        return data
    
    def get_table_row(self, table_locator: str, row_index: int) -> List[str]:
        """Get specific table row data."""
        row = self.page.locator(f"{table_locator} >> tr").nth(row_index)
        cells = row.locator("td, th").all()
        return [cell.text_content() or "" for cell in cells]
    
    def get_table_cell(self, table_locator: str, row: int, col: int) -> str:
        """Get specific table cell text."""
        cell = self.page.locator(f"{table_locator} >> tr").nth(row).locator("td, th").nth(col)
        return cell.text_content() or ""
    
    # ==================== MULTI-ELEMENT ====================
    
    def find_elements(self, locator: str) -> List[Any]:
        """Find multiple elements."""
        return self.page.locator(locator).all()
    
    def get_element_count(self, locator: str) -> int:
        """Get count of matching elements."""
        return self.page.locator(locator).count()
    
    @property
    def framework_name(self) -> str:
        return "playwright"


class SeleniumAdapter(FrameworkAdapter):
    """
    Adapter for Selenium framework with support for ALL UI element types.
    
    Supports:
    - All standard locators (CSS, XPath, ID, Name, etc.)
    - Form controls (inputs, checkboxes, radios, selects, file uploads)
    - Hover interactions (using ActionChains)
    - Dynamic elements (waits, tables, modals)
    - Explicit waits for visibility
    """
    
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
        Find element using ANY locator type.
        
        Supported locator types:
        - XPath: //button[@id='submit'] or xpath=//button
        - CSS: button#submit or css=button#submit
        - ID: id=submit
        - Name: name=username
        - Class: class=btn-primary
        - Tag: tag=button
        - Link Text: link=Click Here
        - Partial Link: partial_link=Click
        - Auto-detect: Automatically detects type if no prefix
        """
        from selenium.webdriver.common.by import By
        
        # Handle explicit prefixes (e.g., "id=submit", "xpath=//button")
        if "=" in locator and not locator.startswith("//"):
            prefix, value = locator.split("=", 1)
            prefix = prefix.lower().strip()
            
            locator_map = {
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "classname": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "tagname": By.TAG_NAME,
                "link": By.LINK_TEXT,
                "linktext": By.LINK_TEXT,
                "link_text": By.LINK_TEXT,
                "partial": By.PARTIAL_LINK_TEXT,
                "partial_link": By.PARTIAL_LINK_TEXT,
                "partiallink": By.PARTIAL_LINK_TEXT,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR,
            }
            
            if prefix in locator_map:
                return self.driver.find_element(locator_map[prefix], value)
        
        # Auto-detect locator type
        locator = locator.strip()
        
        # XPath (starts with // or (// )
        if locator.startswith("//") or locator.startswith("(//"):
            return self.driver.find_element(By.XPATH, locator)
        
        # ID shorthand (#id)
        elif locator.startswith("#") and " " not in locator and ">" not in locator:
            # Simple ID like #submit
            id_value = locator[1:]
            return self.driver.find_element(By.ID, id_value)
        
        # Class shorthand (.classname) - single class only
        elif locator.startswith(".") and " " not in locator and ">" not in locator:
            class_value = locator[1:]
            return self.driver.find_element(By.CLASS_NAME, class_value)
        
        # Default to CSS selector (most flexible)
        else:
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
    
    # ==================== FORM CONTROLS ====================
    
    def check_checkbox(self, locator: str):
        """Check a checkbox."""
        element = self.find_element(locator)
        if not element.is_selected():
            element.click()
    
    def uncheck_checkbox(self, locator: str):
        """Uncheck a checkbox."""
        element = self.find_element(locator)
        if element.is_selected():
            element.click()
    
    def is_checked(self, locator: str) -> bool:
        """Check if checkbox/radio is checked."""
        element = self.find_element(locator)
        return element.is_selected()
    
    def select_radio(self, locator: str):
        """Select a radio button."""
        element = self.find_element(locator)
        if not element.is_selected():
            element.click()
    
    def select_dropdown(self, locator: str, value: str, by: str = "value"):
        """
        Select dropdown option.
        
        Args:
            locator: Dropdown locator
            value: Value to select
            by: Selection method - "value", "text", or "index"
        """
        from selenium.webdriver.support.select import Select
        
        element = self.find_element(locator)
        select = Select(element)
        
        if by == "value":
            select.select_by_value(value)
        elif by == "text" or by == "label":
            select.select_by_visible_text(value)
        elif by == "index":
            select.select_by_index(int(value))
    
    def get_selected_option(self, locator: str) -> str:
        """Get selected dropdown option text."""
        from selenium.webdriver.support.select import Select
        
        element = self.find_element(locator)
        select = Select(element)
        return select.first_selected_option.text
    
    def upload_file(self, locator: str, file_path: str):
        """Upload file to file input."""
        element = self.find_element(locator)
        element.send_keys(file_path)
    
    # ==================== HOVER & VISIBILITY ====================
    
    def hover(self, locator: str):
        """Hover over element (for tooltips, dropdowns)."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()
    
    def wait_for_visible(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be visible."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        try:
            # Parse locator to By strategy
            by, value = self._parse_locator_to_by(locator)
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except:
            return False
    
    def wait_for_hidden(self, locator: str, timeout: int = 10) -> bool:
        """Wait for element to be hidden."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        try:
            by, value = self._parse_locator_to_by(locator)
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((by, value))
            )
            return True
        except:
            return False
    
    def is_enabled(self, locator: str) -> bool:
        """Check if element is enabled."""
        element = self.find_element(locator)
        return element.is_enabled()
    
    # ==================== ATTRIBUTES & PROPERTIES ====================
    
    def get_attribute(self, locator: str, attribute: str) -> Optional[str]:
        """Get element attribute value."""
        element = self.find_element(locator)
        return element.get_attribute(attribute)
    
    def get_property(self, locator: str, property_name: str) -> Any:
        """Get element property value."""
        element = self.find_element(locator)
        return element.get_property(property_name)
    
    def get_value(self, locator: str) -> str:
        """Get input/textarea value."""
        element = self.find_element(locator)
        return element.get_attribute("value") or ""
    
    # ==================== ACTIONS ====================
    
    def double_click(self, locator: str):
        """Double-click element."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        element = self.find_element(locator)
        ActionChains(self.driver).double_click(element).perform()
    
    def right_click(self, locator: str):
        """Right-click element (context menu)."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        element = self.find_element(locator)
        ActionChains(self.driver).context_click(element).perform()
    
    def drag_and_drop(self, source_locator: str, target_locator: str):
        """Drag and drop from source to target."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        source = self.find_element(source_locator)
        target = self.find_element(target_locator)
        ActionChains(self.driver).drag_and_drop(source, target).perform()
    
    def scroll_into_view(self, locator: str):
        """Scroll element into view."""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def press_key(self, locator: str, key: str):
        """Press keyboard key on element."""
        from selenium.webdriver.common.keys import Keys
        
        element = self.find_element(locator)
        
        # Map common key names to Selenium Keys
        key_map = {
            "Enter": Keys.ENTER,
            "Escape": Keys.ESCAPE,
            "Tab": Keys.TAB,
            "Space": Keys.SPACE,
            "ArrowDown": Keys.ARROW_DOWN,
            "ArrowUp": Keys.ARROW_UP,
            "ArrowLeft": Keys.ARROW_LEFT,
            "ArrowRight": Keys.ARROW_RIGHT,
            "Backspace": Keys.BACKSPACE,
            "Delete": Keys.DELETE,
        }
        
        selenium_key = key_map.get(key, key)
        element.send_keys(selenium_key)
    
    # ==================== CONTAINERS & MODALS ====================
    
    def is_modal_open(self, locator: str = "[role='dialog']") -> bool:
        """Check if modal/dialog is open."""
        return self.is_visible(locator)
    
    def close_modal(self, locator: str = "[role='dialog']"):
        """Close modal/dialog (try Escape key or close button)."""
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.by import By
        
        try:
            # Try pressing Escape on body
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except:
            # Try finding and clicking close button
            try:
                close_btn = f"{locator} button[aria-label='Close']"
                if self.is_visible(close_btn):
                    self.click(close_btn)
            except:
                pass
    
    # ==================== TABLES ====================
    
    def get_table_data(self, locator: str) -> List[List[str]]:
        """Get all table data as 2D array."""
        from selenium.webdriver.common.by import By
        
        table = self.find_element(locator)
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td, th")
            row_data = [cell.text for cell in cells]
            data.append(row_data)
        return data
    
    def get_table_row(self, table_locator: str, row_index: int) -> List[str]:
        """Get specific table row data."""
        from selenium.webdriver.common.by import By
        
        table = self.find_element(table_locator)
        rows = table.find_elements(By.TAG_NAME, "tr")
        if row_index < len(rows):
            cells = rows[row_index].find_elements(By.CSS_SELECTOR, "td, th")
            return [cell.text for cell in cells]
        return []
    
    def get_table_cell(self, table_locator: str, row: int, col: int) -> str:
        """Get specific table cell text."""
        from selenium.webdriver.common.by import By
        
        table = self.find_element(table_locator)
        rows = table.find_elements(By.TAG_NAME, "tr")
        if row < len(rows):
            cells = rows[row].find_elements(By.CSS_SELECTOR, "td, th")
            if col < len(cells):
                return cells[col].text
        return ""
    
    # ==================== MULTI-ELEMENT ====================
    
    def find_elements(self, locator: str) -> List[Any]:
        """Find multiple elements."""
        from selenium.webdriver.common.by import By
        
        by, value = self._parse_locator_to_by(locator)
        return self.driver.find_elements(by, value)
    
    def get_element_count(self, locator: str) -> int:
        """Get count of matching elements."""
        return len(self.find_elements(locator))
    
    # ==================== HELPER METHODS ====================
    
    def _parse_locator_to_by(self, locator: str):
        """Parse locator string to (By, value) tuple for WebDriverWait."""
        from selenium.webdriver.common.by import By
        
        if "=" in locator and not locator.startswith("//"):
            prefix, value = locator.split("=", 1)
            prefix = prefix.lower().strip()
            
            locator_map = {
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "classname": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "tagname": By.TAG_NAME,
                "link": By.LINK_TEXT,
                "linktext": By.LINK_TEXT,
                "link_text": By.LINK_TEXT,
                "partial": By.PARTIAL_LINK_TEXT,
                "partial_link": By.PARTIAL_LINK_TEXT,
                "partiallink": By.PARTIAL_LINK_TEXT,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR,
            }
            
            if prefix in locator_map:
                return (locator_map[prefix], value)
        
        locator = locator.strip()
        
        if locator.startswith("//") or locator.startswith("(//"):
            return (By.XPATH, locator)
        elif locator.startswith("#") and " " not in locator and ">" not in locator:
            return (By.ID, locator[1:])
        elif locator.startswith(".") and " " not in locator and ">" not in locator:
            return (By.CLASS_NAME, locator[1:])
        else:
            return (By.CSS_SELECTOR, locator)
    
    @property
    def framework_name(self) -> str:
        return "selenium"
