# 🚀 SmartLocator Quick API Reference

**Complete method reference for all UI element interactions**

---

## 📚 Core Methods

### Basic Interactions
```python
locator.click()                              # Click element
locator.fill(text)                           # Fill text input
locator.text()                               # Get element text
locator.is_visible()                         # Check if visible
```

---

## 📝 Form Controls

### Text Inputs
```python
locator.fill("text")                         # Fill text input
locator.get_value()                          # Get current value
locator.is_enabled()                         # Check if enabled
```

### Checkboxes
```python
locator.check()                              # Check checkbox
locator.uncheck()                            # Uncheck checkbox
locator.is_checked()                         # Check if checked (returns bool)
```

### Radio Buttons
```python
locator.check()                              # Select radio button
locator.is_checked()                         # Check if selected
```

### Dropdowns
```python
locator.select_option("value", by="value")   # Select by value
locator.select_option("Text", by="label")    # Select by visible text
locator.select_option("0", by="index")       # Select by index (0-based)
locator.get_selected_option()                # Get selected option text
```

### File Upload
```python
locator.upload_file("C:/path/to/file.pdf")   # Upload file
```

---

## 🎯 Actions

### Mouse Actions
```python
locator.click()                              # Single click
locator.double_click()                       # Double click
locator.right_click()                        # Right-click (context menu)
locator.hover()                              # Hover over element
```

### Drag & Drop
```python
source.drag_to(target_locator)               # Drag source to target
```

### Keyboard
```python
locator.press_key("Enter")                   # Press Enter
locator.press_key("Escape")                  # Press Escape
locator.press_key("Tab")                     # Press Tab
locator.press_key("ArrowDown")               # Press Arrow Down
locator.press_key("ArrowUp")                 # Press Arrow Up
```

### Scroll
```python
locator.scroll_into_view()                   # Scroll element into view
```

---

## 👁️ Visibility & Waits

### Wait Operations
```python
locator.wait_visible(timeout=10)             # Wait for visible (seconds)
locator.wait_hidden(timeout=10)              # Wait for hidden (seconds)
```

### Visibility Checks
```python
locator.is_visible()                         # Check if visible (returns bool)
locator.is_enabled()                         # Check if enabled (returns bool)
```

---

## 🔍 Attributes & Properties

### Get Values
```python
locator.get_attribute("href")                # Get HTML attribute
locator.get_attribute("class")               # Get class attribute
locator.get_attribute("aria-selected")       # Get ARIA attribute
locator.get_attribute("data-id")             # Get data attribute

locator.get_property("value")                # Get property (JS)
locator.get_value()                          # Get input value (shortcut)
```

---

## 📦 Containers

### Modals
```python
modal.wait_visible(timeout=5)                # Wait for modal to appear
modal.is_visible()                           # Check if modal is open
modal.press_key("Escape")                    # Close modal with Escape

close_btn = SmartLocator("button.close", adapter)
close_btn.click()                            # Close via button
modal.wait_hidden(timeout=5)                 # Wait for modal to close
```

---

## 📊 Tables

### Table Data Extraction
```python
# Use adapter methods for table operations
from core.smart_locator import PlaywrightAdapter

adapter = PlaywrightAdapter(page)

# Get all table data as 2D array
data = adapter.get_table_data("table#users")
# Returns: [["Cell1", "Cell2"], ["Cell3", "Cell4"], ...]

# Get specific row (0-indexed)
row = adapter.get_table_row("table#users", 0)
# Returns: ["Cell1", "Cell2", "Cell3"]

# Get specific cell (row_index, col_index)
cell = adapter.get_table_cell("table#users", 0, 1)
# Returns: "Cell2"
```

### Table Interactions
```python
# Click table row
row = SmartLocator("table tr:nth-child(2)", adapter)
row.click()

# Sort by column
header = SmartLocator("table th:nth-child(1)", adapter)
header.click()

# Navigate pages
next_btn = SmartLocator("button[aria-label='Next']", adapter)
next_btn.click()
```

---

## 🔢 Multi-Element Operations

### Count Elements
```python
items = SmartLocator(".product-card", adapter)
total = items.count()                        # Returns: int (number of elements)
print(f"Found {total} products")
```

### Iterate Elements
```python
items = SmartLocator(".list-item", adapter)
total = items.count()

for i in range(total):
    item = SmartLocator(f".list-item:nth-child({i+1})", adapter)
    text = item.text()
    print(f"Item {i+1}: {text}")
```

---

## ♿ ARIA Roles

### Common ARIA Locators
```python
# Dialog
dialog = SmartLocator("role=dialog", adapter)

# Alert
alert = SmartLocator("role=alert", adapter)

# Combobox (autocomplete)
combobox = SmartLocator("role=combobox", adapter)

# Menu
menu = SmartLocator("role=menu", adapter)
menu_item = SmartLocator("role=menuitem[name='Save']", adapter)

# Listbox
listbox = SmartLocator("role=listbox", adapter)
option = SmartLocator("role=option[name='Option 1']", adapter)

# Tab
tab = SmartLocator("role=tab[name='Profile']", adapter)
tab_panel = SmartLocator("role=tabpanel", adapter)

# Tree
tree = SmartLocator("role=tree", adapter)
tree_item = SmartLocator("role=treeitem[name='Documents']", adapter)

# Grid
grid = SmartLocator("role=grid", adapter)
grid_cell = SmartLocator("role=gridcell", adapter)
```

---

## 🎨 Common Patterns

### Hover Then Click
```python
# Hover to reveal submenu
menu.hover()

# Wait for submenu
submenu = SmartLocator(".submenu", adapter)
submenu.wait_visible()

# Click item
item.click()
```

### Wait Then Interact
```python
# Wait for loading to finish
loading.wait_hidden(timeout=30)

# Then interact
button.wait_visible()
button.click()
```

### Modal Workflow
```python
# Open modal
button.click()

# Wait for modal
modal.wait_visible(timeout=5)

# Interact with modal content
input_field = SmartLocator("role=dialog >> input", adapter)
input_field.fill("value")

# Submit
submit_btn = SmartLocator("role=dialog >> button[type='submit']", adapter)
submit_btn.click()

# Wait for modal to close
modal.wait_hidden(timeout=5)
```

### Form Filling
```python
# Fill form fields
username.fill("john.doe")
email.fill("john@example.com")
country.select_option("US", by="value")

# Check checkbox
terms.check()

# Upload file
file_input.upload_file("C:/path/to/file.pdf")

# Submit
submit_btn.click()

# Wait for success
success_msg.wait_visible(timeout=10)
```

### Table Data Extraction
```python
# Get all table data
from core.smart_locator import PlaywrightAdapter
adapter = PlaywrightAdapter(page)

all_data = adapter.get_table_data("table#users")

# Process data
for row_index, row_data in enumerate(all_data):
    print(f"Row {row_index}: {row_data}")
    
    # Get specific cell
    cell_value = row_data[2]  # Third column
    print(f"Cell value: {cell_value}")
```

### Autocomplete Selection
```python
# Type in autocomplete
search.fill("New Y")

# Wait for suggestions
suggestions.wait_visible()

# Navigate with keyboard
search.press_key("ArrowDown")
search.press_key("ArrowDown")
search.press_key("Enter")

# Or click specific option
option = SmartLocator("role=option[name='New York']", adapter)
option.click()
```

### Drag and Drop
```python
# Drag item to target
source = SmartLocator(".draggable", adapter)
target = SmartLocator(".drop-zone", adapter)

source.drag_to(target.get_current_locator())
```

---

## 🏗️ Adapter-Specific Methods

### PlaywrightAdapter
```python
adapter = PlaywrightAdapter(page)

# All SmartLocator methods available
locator = SmartLocator("#id", adapter, "Description")
```

### SeleniumAdapter
```python
adapter = SeleniumAdapter(driver)

# All SmartLocator methods available
locator = SmartLocator("#id", adapter, "Description")
```

---

## 🔧 Framework-Agnostic Usage

**Same API works for both Playwright and Selenium!**

```python
# Playwright
from playwright.sync_api import sync_playwright
from core.smart_locator import SmartLocator, PlaywrightAdapter

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    adapter = PlaywrightAdapter(page)
    
    locator = SmartLocator("#button", adapter, "Button")
    locator.click()  # Works!

# Selenium
from selenium import webdriver
from core.smart_locator import SmartLocator, SeleniumAdapter

driver = webdriver.Chrome()
adapter = SeleniumAdapter(driver)

locator = SmartLocator("#button", adapter, "Button")
locator.click()  # Same API!
```

---

## ✅ Return Types

| Method | Return Type | Example |
|--------|------------|---------|
| `click()` | None | - |
| `fill(text)` | None | - |
| `text()` | str | `"Button Text"` |
| `is_visible()` | bool | `True` / `False` |
| `is_checked()` | bool | `True` / `False` |
| `is_enabled()` | bool | `True` / `False` |
| `get_value()` | str | `"input value"` |
| `get_attribute(name)` | str | `"href-value"` |
| `get_selected_option()` | str | `"Selected Text"` |
| `count()` | int | `5` |
| `get_table_data(locator)` | List[List[str]] | `[["A", "B"], ["C", "D"]]` |
| `get_table_row(locator, index)` | List[str] | `["Cell1", "Cell2"]` |
| `get_table_cell(locator, row, col)` | str | `"Cell value"` |

---

## 🚀 AI Auto-Healing

**ALL methods have automatic AI-powered healing!**

```python
# Locator breaks? No problem!
button = SmartLocator("#old-id", adapter, "Submit button")

# This automatically heals if #old-id changes
button.click()  # ✅ Still works via AI healing!

# AI finds: button[type='submit'], .btn-primary, etc.
```

---

## 📖 Documentation

- **Complete Guide**: `docs/COMPLETE_UI_ELEMENTS_GUIDE.md`
- **Locator Types**: `docs/LOCATOR_TYPES_GUIDE.md`
- **Demo Tests**: `tests/test_ui_elements_comprehensive.py`
- **REST API**: `docs/API_QUICK_START.md`

---

**Framework by: Ram, Senior AI Test Automation Engineer** 🎯

**40+ methods | 2 frameworks | 100% AI-healing coverage**
