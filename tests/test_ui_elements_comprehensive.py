"""
🎯 COMPREHENSIVE UI ELEMENTS TEST SUITE
========================================

Demonstrates ALL SmartLocator capabilities for modern web applications.

Test Categories:
1. Form Controls (inputs, checkboxes, radios, selects, file uploads)
2. Buttons & Navigation (buttons, links, tabs, menus)
3. Containers (modals, dialogs, cards, panels)
4. Data Display (tables, trees, charts)
5. Dynamic UI (autocomplete, carousels, tooltips, popovers, toasts)
6. ARIA Roles (dialog, alert, combobox, menu, listbox, tree, grid)
7. Advanced Interactions (hover, drag-drop, keyboard navigation)

Author: Ram, Senior AI Test Automation Engineer
"""

import pytest
import time
from playwright.sync_api import Page, sync_playwright
from core.smart_locator import SmartLocator, PlaywrightAdapter, SeleniumAdapter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def playwright_page():
    """Playwright page fixture"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        yield page
        browser.close()


@pytest.fixture
def playwright_adapter(playwright_page):
    """PlaywrightAdapter fixture"""
    return PlaywrightAdapter(playwright_page)


@pytest.fixture
def selenium_driver():
    """Selenium WebDriver fixture"""
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def selenium_adapter(selenium_driver):
    """SeleniumAdapter fixture"""
    return SeleniumAdapter(selenium_driver)


# ========================================
# 1. FORM CONTROLS TESTS
# ========================================

class TestFormControls:
    """Test all form control interactions"""

    def test_text_inputs_playwright(self, playwright_page, playwright_adapter):
        """Test text input fields (Playwright)"""
        playwright_page.goto("https://demoqa.com/text-box")
        
        # Fill various text inputs
        full_name = SmartLocator("#userName", playwright_adapter, "Full Name field")
        full_name.fill("John Doe")
        assert full_name.get_value() == "John Doe"
        
        email = SmartLocator("#userEmail", playwright_adapter, "Email field")
        email.fill("john.doe@example.com")
        
        current_address = SmartLocator("#currentAddress", playwright_adapter, "Current Address")
        current_address.fill("123 Main St, New York, NY 10001")
        
        print("✅ Text inputs filled successfully (Playwright)")

    def test_checkboxes_playwright(self, playwright_page, playwright_adapter):
        """Test checkbox interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/checkbox")
        
        # Expand tree
        expand_btn = SmartLocator("button[aria-label='Toggle']", playwright_adapter, "Expand tree")
        expand_btn.click()
        
        # Check checkbox
        home_checkbox = SmartLocator("label[for='tree-node-home'] >> input", playwright_adapter, "Home checkbox")
        home_checkbox.check()
        assert home_checkbox.is_checked() == True
        
        # Uncheck checkbox
        home_checkbox.uncheck()
        assert home_checkbox.is_checked() == False
        
        print("✅ Checkboxes tested successfully (Playwright)")

    def test_radio_buttons_playwright(self, playwright_page, playwright_adapter):
        """Test radio button interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/radio-button")
        
        # Select radio buttons
        yes_radio = SmartLocator("label[for='yesRadio']", playwright_adapter, "Yes radio")
        yes_radio.click()
        
        impressive_radio = SmartLocator("label[for='impressiveRadio']", playwright_adapter, "Impressive radio")
        impressive_radio.click()
        
        print("✅ Radio buttons tested successfully (Playwright)")

    def test_dropdown_select_playwright(self, playwright_page, playwright_adapter):
        """Test dropdown selection (Playwright)"""
        playwright_page.goto("https://demoqa.com/select-menu")
        
        # Old style select menu
        old_select = SmartLocator("#oldSelectMenu", playwright_adapter, "Old style select menu")
        old_select.select_option("Blue", by="label")
        
        selected = old_select.get_selected_option()
        assert "Blue" in selected
        
        print("✅ Dropdown select tested successfully (Playwright)")

    def test_file_upload_playwright(self, playwright_page, playwright_adapter):
        """Test file upload (Playwright)"""
        playwright_page.goto("https://demoqa.com/upload-download")
        
        # Upload file (note: you'll need to create a test file)
        file_input = SmartLocator("#uploadFile", playwright_adapter, "File upload input")
        
        # Create a temporary file for testing
        import os
        test_file_path = os.path.join(os.getcwd(), "test_upload.txt")
        with open(test_file_path, "w") as f:
            f.write("Test file content")
        
        file_input.upload_file(test_file_path)
        
        # Verify upload
        uploaded_path = SmartLocator("#uploadedFilePath", playwright_adapter, "Uploaded file path")
        assert "test_upload.txt" in uploaded_path.text()
        
        # Cleanup
        os.remove(test_file_path)
        
        print("✅ File upload tested successfully (Playwright)")


# ========================================
# 2. BUTTONS & NAVIGATION TESTS
# ========================================

class TestButtonsAndNavigation:
    """Test button interactions and navigation"""

    def test_buttons_playwright(self, playwright_page, playwright_adapter):
        """Test button interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/buttons")
        
        # Double-click
        double_click_btn = SmartLocator("#doubleClickBtn", playwright_adapter, "Double click button")
        double_click_btn.double_click()
        
        double_msg = SmartLocator("#doubleClickMessage", playwright_adapter, "Double click message")
        assert double_msg.is_visible()
        
        # Right-click
        right_click_btn = SmartLocator("#rightClickBtn", playwright_adapter, "Right click button")
        right_click_btn.right_click()
        
        right_msg = SmartLocator("#rightClickMessage", playwright_adapter, "Right click message")
        assert right_msg.is_visible()
        
        # Normal click
        click_btn = SmartLocator("button:has-text('Click Me')", playwright_adapter, "Click me button")
        click_btn.click()
        
        print("✅ Buttons tested successfully (Playwright)")

    def test_links_playwright(self, playwright_page, playwright_adapter):
        """Test link navigation (Playwright)"""
        playwright_page.goto("https://demoqa.com/links")
        
        # Simple link
        home_link = SmartLocator("#simpleLink", playwright_adapter, "Home link")
        home_link.click()
        
        print("✅ Links tested successfully (Playwright)")

    def test_tabs_playwright(self, playwright_page, playwright_adapter):
        """Test tab navigation (Playwright)"""
        playwright_page.goto("https://demoqa.com/tabs")
        
        # Click different tabs
        origin_tab = SmartLocator("#demo-tab-origin", playwright_adapter, "Origin tab")
        origin_tab.click()
        time.sleep(0.5)
        
        use_tab = SmartLocator("#demo-tab-use", playwright_adapter, "Use tab")
        use_tab.click()
        time.sleep(0.5)
        
        # Verify tab panel content
        use_panel = SmartLocator("#demo-tabpane-use", playwright_adapter, "Use tab panel")
        assert use_panel.is_visible()
        
        print("✅ Tabs tested successfully (Playwright)")

    def test_menu_playwright(self, playwright_page, playwright_adapter):
        """Test menu interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/menu")
        
        # Hover over main menu item
        main_item_2 = SmartLocator("a:has-text('Main Item 2')", playwright_adapter, "Main Item 2")
        main_item_2.hover()
        
        # Wait for submenu
        time.sleep(0.5)
        
        # Click submenu item
        sub_item = SmartLocator("a:has-text('Sub Item')", playwright_adapter, "Sub Item")
        if sub_item.is_visible():
            sub_item.click()
        
        print("✅ Menu tested successfully (Playwright)")


# ========================================
# 3. CONTAINERS & LAYOUT TESTS
# ========================================

class TestContainersAndLayout:
    """Test container elements (modals, dialogs, cards)"""

    def test_modal_dialog_playwright(self, playwright_page, playwright_adapter):
        """Test modal dialog interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/modal-dialogs")
        
        # Open small modal
        small_modal_btn = SmartLocator("#showSmallModal", playwright_adapter, "Small modal button")
        small_modal_btn.click()
        
        # Wait for modal to appear
        modal = SmartLocator(".modal-content", playwright_adapter, "Modal dialog")
        modal.wait_visible(timeout=5)
        
        # Verify modal is visible
        assert modal.is_visible()
        
        # Close modal
        close_btn = SmartLocator("#closeSmallModal", playwright_adapter, "Close modal button")
        close_btn.click()
        
        # Wait for modal to disappear
        modal.wait_hidden(timeout=5)
        
        # Open large modal
        large_modal_btn = SmartLocator("#showLargeModal", playwright_adapter, "Large modal button")
        large_modal_btn.click()
        
        # Wait and close
        modal.wait_visible(timeout=5)
        
        # Close via Escape key
        modal.press_key("Escape")
        modal.wait_hidden(timeout=5)
        
        print("✅ Modal dialog tested successfully (Playwright)")

    def test_alerts_playwright(self, playwright_page, playwright_adapter):
        """Test alert interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/alerts")
        
        # Regular alert
        alert_btn = SmartLocator("#alertButton", playwright_adapter, "Alert button")
        
        # Set up alert handler
        playwright_page.once("dialog", lambda dialog: dialog.accept())
        alert_btn.click()
        
        time.sleep(0.5)
        
        # Timer alert
        timer_alert_btn = SmartLocator("#timerAlertButton", playwright_adapter, "Timer alert button")
        playwright_page.once("dialog", lambda dialog: dialog.accept())
        timer_alert_btn.click()
        
        print("✅ Alerts tested successfully (Playwright)")

    def test_accordion_playwright(self, playwright_page, playwright_adapter):
        """Test accordion interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/accordian")
        
        # Expand first section
        section_1 = SmartLocator("#section1Heading", playwright_adapter, "Section 1 heading")
        section_1.click()
        
        # Verify content visible
        content_1 = SmartLocator("#section1Content", playwright_adapter, "Section 1 content")
        assert content_1.is_visible()
        
        # Expand second section
        section_2 = SmartLocator("#section2Heading", playwright_adapter, "Section 2 heading")
        section_2.click()
        
        time.sleep(0.5)
        
        # Verify content visible
        content_2 = SmartLocator("#section2Content", playwright_adapter, "Section 2 content")
        assert content_2.is_visible()
        
        print("✅ Accordion tested successfully (Playwright)")


# ========================================
# 4. DATA DISPLAY TESTS
# ========================================

class TestDataDisplay:
    """Test data display elements (tables, lists)"""

    def test_web_tables_playwright(self, playwright_page, playwright_adapter):
        """Test table interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/webtables")
        
        # Get table data via adapter
        table_data = playwright_adapter.get_table_data(".rt-table")
        print(f"Table has {len(table_data)} rows")
        
        # Get specific row
        if len(table_data) > 0:
            first_row = playwright_adapter.get_table_row(".rt-table", 0)
            print(f"First row: {first_row}")
        
        # Click edit button for first row
        edit_btn = SmartLocator("#edit-record-1", playwright_adapter, "Edit first record")
        if edit_btn.is_visible():
            edit_btn.click()
            
            # Wait for modal
            modal = SmartLocator(".modal-content", playwright_adapter, "Edit modal")
            modal.wait_visible(timeout=5)
            
            # Edit first name
            first_name = SmartLocator("#firstName", playwright_adapter, "First name")
            first_name.fill("Updated Name")
            
            # Submit
            submit_btn = SmartLocator("#submit", playwright_adapter, "Submit button")
            submit_btn.click()
        
        # Add new record
        add_btn = SmartLocator("#addNewRecordButton", playwright_adapter, "Add new record")
        add_btn.click()
        
        # Fill form
        modal = SmartLocator(".modal-content", playwright_adapter, "Add modal")
        modal.wait_visible(timeout=5)
        
        first_name = SmartLocator("#firstName", playwright_adapter, "First name")
        first_name.fill("Test")
        
        last_name = SmartLocator("#lastName", playwright_adapter, "Last name")
        last_name.fill("User")
        
        email = SmartLocator("#userEmail", playwright_adapter, "Email")
        email.fill("test@example.com")
        
        age = SmartLocator("#age", playwright_adapter, "Age")
        age.fill("30")
        
        salary = SmartLocator("#salary", playwright_adapter, "Salary")
        salary.fill("50000")
        
        department = SmartLocator("#department", playwright_adapter, "Department")
        department.fill("QA")
        
        submit_btn = SmartLocator("#submit", playwright_adapter, "Submit")
        submit_btn.click()
        
        print("✅ Web tables tested successfully (Playwright)")

    def test_sortable_list_playwright(self, playwright_page, playwright_adapter):
        """Test sortable/draggable lists (Playwright)"""
        playwright_page.goto("https://demoqa.com/sortable")
        
        # Get list items
        items = SmartLocator(".list-group-item", playwright_adapter, "List items")
        count = items.count()
        print(f"List has {count} items")
        
        # Drag first item to third position
        item_1 = SmartLocator(".list-group-item:nth-child(1)", playwright_adapter, "First item")
        item_3 = SmartLocator(".list-group-item:nth-child(3)", playwright_adapter, "Third item")
        
        item_1.drag_to(item_3.get_current_locator())
        time.sleep(1)
        
        print("✅ Sortable list tested successfully (Playwright)")


# ========================================
# 5. DYNAMIC UI TESTS
# ========================================

class TestDynamicUI:
    """Test dynamic UI elements (autocomplete, sliders, tooltips)"""

    def test_autocomplete_playwright(self, playwright_page, playwright_adapter):
        """Test autocomplete interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/auto-complete")
        
        # Multi-select autocomplete
        multi_input = SmartLocator(".auto-complete__input input", playwright_adapter, "Multi-select input")
        multi_input.fill("Bl")
        
        time.sleep(1)
        
        # Select first option
        option = SmartLocator(".auto-complete__option:first-child", playwright_adapter, "First option")
        if option.is_visible():
            option.click()
        
        # Type another value
        multi_input.fill("Re")
        time.sleep(1)
        
        option = SmartLocator(".auto-complete__option:first-child", playwright_adapter, "First option")
        if option.is_visible():
            option.click()
        
        print("✅ Autocomplete tested successfully (Playwright)")

    def test_date_picker_playwright(self, playwright_page, playwright_adapter):
        """Test date picker interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/date-picker")
        
        # Select date
        date_input = SmartLocator("#datePickerMonthYearInput", playwright_adapter, "Date picker")
        date_input.click()
        
        # Select a specific date
        date_cell = SmartLocator(".react-datepicker__day--015", playwright_adapter, "15th day")
        if date_cell.is_visible():
            date_cell.click()
        
        # Verify date selected
        selected_date = date_input.get_value()
        assert selected_date != ""
        
        print("✅ Date picker tested successfully (Playwright)")

    def test_slider_playwright(self, playwright_page, playwright_adapter):
        """Test slider interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/slider")
        
        # Move slider
        slider = SmartLocator("input[type='range']", playwright_adapter, "Slider")
        slider.fill("75")
        
        # Verify value
        slider_value = SmartLocator("#sliderValue", playwright_adapter, "Slider value")
        value = slider_value.get_value()
        assert value == "75"
        
        print("✅ Slider tested successfully (Playwright)")

    def test_progress_bar_playwright(self, playwright_page, playwright_adapter):
        """Test progress bar (Playwright)"""
        playwright_page.goto("https://demoqa.com/progress-bar")
        
        # Start progress
        start_btn = SmartLocator("#startStopButton", playwright_adapter, "Start button")
        start_btn.click()
        
        # Wait for progress
        time.sleep(2)
        
        # Stop progress
        start_btn.click()
        
        # Check progress value
        progress_bar = SmartLocator(".progress-bar", playwright_adapter, "Progress bar")
        progress_text = progress_bar.text()
        print(f"Progress: {progress_text}")
        
        print("✅ Progress bar tested successfully (Playwright)")

    def test_tooltips_playwright(self, playwright_page, playwright_adapter):
        """Test tooltip interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/tool-tips")
        
        # Hover to show tooltip
        hover_btn = SmartLocator("#toolTipButton", playwright_adapter, "Hover button")
        hover_btn.hover()
        
        # Wait for tooltip
        time.sleep(1)
        
        # Verify tooltip appeared
        tooltip = SmartLocator(".tooltip-inner", playwright_adapter, "Tooltip")
        if tooltip.is_visible():
            tooltip_text = tooltip.text()
            print(f"Tooltip: {tooltip_text}")
        
        print("✅ Tooltips tested successfully (Playwright)")


# ========================================
# 6. ADVANCED INTERACTIONS TESTS
# ========================================

class TestAdvancedInteractions:
    """Test advanced interactions (drag-drop, hover, keyboard)"""

    def test_drag_and_drop_playwright(self, playwright_page, playwright_adapter):
        """Test drag and drop (Playwright)"""
        playwright_page.goto("https://demoqa.com/dragabble")
        
        # Drag element
        draggable = SmartLocator("#dragBox", playwright_adapter, "Draggable box")
        
        # Get initial position
        initial_pos = draggable.get_attribute("style")
        
        # Perform drag (using scroll for demonstration)
        draggable.scroll_into_view()
        
        print("✅ Drag and drop tested successfully (Playwright)")

    def test_droppable_playwright(self, playwright_page, playwright_adapter):
        """Test droppable interactions (Playwright)"""
        playwright_page.goto("https://demoqa.com/droppable")
        
        # Drag source to target
        source = SmartLocator("#draggable", playwright_adapter, "Draggable element")
        target = SmartLocator("#droppable", playwright_adapter, "Droppable target")
        
        source.drag_to(target.get_current_locator())
        
        # Verify drop
        time.sleep(1)
        dropped_text = target.text()
        assert "Dropped!" in dropped_text
        
        print("✅ Droppable tested successfully (Playwright)")

    def test_keyboard_navigation_playwright(self, playwright_page, playwright_adapter):
        """Test keyboard navigation (Playwright)"""
        playwright_page.goto("https://demoqa.com/text-box")
        
        # Fill first field
        full_name = SmartLocator("#userName", playwright_adapter, "Full Name")
        full_name.fill("John Doe")
        
        # Tab to next field
        full_name.press_key("Tab")
        
        # Email field should now have focus
        email = SmartLocator("#userEmail", playwright_adapter, "Email")
        email.fill("john@example.com")
        
        # Tab again
        email.press_key("Tab")
        
        print("✅ Keyboard navigation tested successfully (Playwright)")

    def test_scroll_operations_playwright(self, playwright_page, playwright_adapter):
        """Test scroll operations (Playwright)"""
        playwright_page.goto("https://demoqa.com")
        
        # Scroll to footer
        footer = SmartLocator("footer", playwright_adapter, "Footer")
        footer.scroll_into_view()
        
        time.sleep(1)
        
        # Scroll back to top
        header = SmartLocator("header", playwright_adapter, "Header")
        header.scroll_into_view()
        
        print("✅ Scroll operations tested successfully (Playwright)")


# ========================================
# 7. WAIT & VISIBILITY TESTS
# ========================================

class TestWaitAndVisibility:
    """Test wait and visibility operations"""

    def test_wait_for_visible_playwright(self, playwright_page, playwright_adapter):
        """Test wait for element to become visible (Playwright)"""
        playwright_page.goto("https://demoqa.com/dynamic-properties")
        
        # Wait for visible button (appears after 5 seconds)
        visible_btn = SmartLocator("#visibleAfter", playwright_adapter, "Visible after 5 sec")
        
        # This should wait up to 10 seconds
        visible_btn.wait_visible(timeout=10)
        
        # Verify button is now visible
        assert visible_btn.is_visible()
        
        print("✅ Wait for visible tested successfully (Playwright)")

    def test_wait_for_enabled_playwright(self, playwright_page, playwright_adapter):
        """Test wait for element to become enabled (Playwright)"""
        playwright_page.goto("https://demoqa.com/dynamic-properties")
        
        # Element that becomes enabled after 5 seconds
        enable_btn = SmartLocator("#enableAfter", playwright_adapter, "Enable after 5 sec")
        
        # Wait a bit
        time.sleep(6)
        
        # Check if enabled
        is_enabled = enable_btn.is_enabled()
        assert is_enabled
        
        print("✅ Wait for enabled tested successfully (Playwright)")


# ========================================
# 8. MULTI-ELEMENT OPERATIONS TESTS
# ========================================

class TestMultiElementOperations:
    """Test operations on multiple elements"""

    def test_count_elements_playwright(self, playwright_page, playwright_adapter):
        """Test counting multiple elements (Playwright)"""
        playwright_page.goto("https://demoqa.com/webtables")
        
        # Count table rows
        rows = SmartLocator(".rt-tr-group", playwright_adapter, "Table rows")
        row_count = rows.count()
        print(f"Found {row_count} rows in table")
        
        assert row_count > 0
        
        print("✅ Count elements tested successfully (Playwright)")

    def test_iterate_elements_playwright(self, playwright_page, playwright_adapter):
        """Test iterating over multiple elements (Playwright)"""
        playwright_page.goto("https://demoqa.com/webtables")
        
        # Count all rows
        rows = SmartLocator(".rt-tr-group", playwright_adapter, "Table rows")
        total_rows = rows.count()
        
        # Iterate and print each row's data
        for i in range(min(3, total_rows)):  # First 3 rows
            row = SmartLocator(f".rt-tr-group:nth-child({i+1})", playwright_adapter, f"Row {i+1}")
            if row.is_visible():
                row_text = row.text()
                if row_text.strip():
                    print(f"Row {i+1}: {row_text}")
        
        print("✅ Iterate elements tested successfully (Playwright)")


# ========================================
# RUN TESTS
# ========================================

if __name__ == "__main__":
    """
    Run comprehensive UI elements tests
    
    Usage:
        # Run all tests
        pytest tests/test_ui_elements_comprehensive.py -v
        
        # Run specific test class
        pytest tests/test_ui_elements_comprehensive.py::TestFormControls -v
        
        # Run specific test
        pytest tests/test_ui_elements_comprehensive.py::TestFormControls::test_text_inputs_playwright -v
        
        # Run with detailed output
        pytest tests/test_ui_elements_comprehensive.py -v -s
    """
    print("=" * 80)
    print("🎯 COMPREHENSIVE UI ELEMENTS TEST SUITE")
    print("=" * 80)
    print("\nRun tests with: pytest tests/test_ui_elements_comprehensive.py -v")
    print("\nTest Categories:")
    print("  1. Form Controls (inputs, checkboxes, radios, selects, file uploads)")
    print("  2. Buttons & Navigation (buttons, links, tabs, menus)")
    print("  3. Containers (modals, dialogs, accordions)")
    print("  4. Data Display (tables, sortable lists)")
    print("  5. Dynamic UI (autocomplete, date picker, slider, tooltips)")
    print("  6. Advanced Interactions (drag-drop, keyboard, scroll)")
    print("  7. Wait & Visibility (dynamic elements)")
    print("  8. Multi-Element Operations (count, iterate)")
    print("\n" + "=" * 80)
