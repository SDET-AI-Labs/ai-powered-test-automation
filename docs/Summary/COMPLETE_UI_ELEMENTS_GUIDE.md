# 🎯 SmartLocator - Complete UI Element Support Guide

**Senior Test Automation Engineer: Ram**

---

## 📋 Overview

SmartLocator now supports **ALL UI element types** with AI-powered auto-healing:

✅ **Form Controls** - inputs, checkboxes, radios, selects, file uploads  
✅ **Buttons & Navigation** - buttons, links, tabs, menus, breadcrumbs  
✅ **Containers & Layout** - modals, dialogs, cards, panels, sidebars  
✅ **Data Display** - tables (static, paginated, sortable), trees, charts  
✅ **Dynamic UI** - autocomplete, carousels, tooltips, popovers, toast notifications  
✅ **Accessibility** - ARIA roles (dialog, alert, combobox, menu, listbox, tree, grid)  
✅ **Hover & Visibility** - hover interactions, wait for visible/hidden  
✅ **Advanced Actions** - double-click, right-click, drag-and-drop, keyboard  

---

## 🎨 Supported UI Element Types

### 1. **Form Controls**

#### Text Inputs
```python
# Standard text input
username = SmartLocator("input[name='username']", adapter, "Username field")
username.fill("john.doe@example.com")

# Password input
password = SmartLocator("input[type='password']", adapter, "Password field")
password.fill("SecretPass123!")

# Textarea
comment = SmartLocator("textarea#comment", adapter, "Comment box")
comment.fill("This is a multi-line comment")

# Number input
age = SmartLocator("input[type='number']", adapter, "Age field")
age.fill("25")

# Email input
email = SmartLocator("input[type='email']", adapter, "Email field")
email.fill("user@example.com")

# Get current value
current_value = username.get_value()
```

#### Checkboxes
```python
# Check checkbox
terms = SmartLocator("input[type='checkbox']#terms", adapter, "Terms checkbox")
terms.check()

# Uncheck checkbox
newsletter = SmartLocator("#newsletter", adapter, "Newsletter checkbox")
newsletter.uncheck()

# Check if checked
if terms.is_checked():
    print("✅ Terms accepted")

# Toggle checkbox
subscribe = SmartLocator("#subscribe", adapter)
if not subscribe.is_checked():
    subscribe.check()
```

#### Radio Buttons
```python
# Select radio button
male = SmartLocator("input[type='radio'][value='male']", adapter, "Gender: Male")
male.check()

female = SmartLocator("input[type='radio'][value='female']", adapter, "Gender: Female")
female.check()

# Check selected
if male.is_checked():
    print("Male selected")
```

#### Dropdowns / Select Elements
```python
# Select by value
country = SmartLocator("select#country", adapter, "Country dropdown")
country.select_option("US", by="value")

# Select by visible text/label
state = SmartLocator("select#state", adapter, "State dropdown")
state.select_option("California", by="label")

# Select by index
month = SmartLocator("select#month", adapter, "Month dropdown")
month.select_option("0", by="index")  # January

# Get selected option
selected_country = country.get_selected_option()
print(f"Selected: {selected_country}")
```

#### File Upload
```python
# Single file upload
file_input = SmartLocator("input[type='file']", adapter, "File upload")
file_input.upload_file("C:/Users/test/document.pdf")

# Drag-and-drop file upload
upload_zone = SmartLocator("[data-testid='drop-zone']", adapter, "Drop zone")
upload_zone.upload_file("C:/Users/test/image.jpg")
```

---

### 2. **Buttons & Navigation**

#### Standard Buttons
```python
# Button element
submit_btn = SmartLocator("button[type='submit']", adapter, "Submit button")
submit_btn.click()

# Input button
reset_btn = SmartLocator("input[type='button']", adapter, "Reset button")
reset_btn.click()

# Link button
cancel_link = SmartLocator("a.btn-cancel", adapter, "Cancel link button")
cancel_link.click()

# Double-click button
edit_btn = SmartLocator("button.edit", adapter, "Edit button")
edit_btn.double_click()

# Right-click for context menu
more_btn = SmartLocator("button.more-options", adapter, "More options")
more_btn.right_click()
```

#### Links & Navigation
```python
# Anchor link
home_link = SmartLocator("a[href='/home']", adapter, "Home link")
home_link.click()

# Nav bar item
products_nav = SmartLocator("nav a[href='/products']", adapter, "Products nav")
products_nav.click()

# Breadcrumb
breadcrumb = SmartLocator(".breadcrumb a:last-child", adapter, "Last breadcrumb")
breadcrumb.click()
```

#### Tabs
```python
# Tab navigation
profile_tab = SmartLocator("role=tab[name='Profile']", adapter, "Profile tab")
profile_tab.click()

settings_tab = SmartLocator("[role='tab'][id='settings']", adapter, "Settings tab")
settings_tab.click()

# Check if tab is active
if profile_tab.get_attribute("aria-selected") == "true":
    print("Profile tab is active")
```

#### Accordions
```python
# Expand accordion
faq_1 = SmartLocator("button[aria-controls='faq-1']", adapter, "FAQ 1")
faq_1.click()

# Check if expanded
is_expanded = faq_1.get_attribute("aria-expanded") == "true"
```

#### Menus
```python
# Open menu
file_menu = SmartLocator("role=button[name='File']", adapter, "File menu")
file_menu.click()

# Select menu item
save_item = SmartLocator("role=menuitem[name='Save']", adapter, "Save menu item")
save_item.click()

# Context menu (right-click)
editor = SmartLocator("#text-editor", adapter, "Text editor")
editor.right_click()

copy_item = SmartLocator("role=menuitem[name='Copy']", adapter, "Copy")
copy_item.click()
```

---

### 3. **Containers & Layout**

#### Modals / Dialogs
```python
# Wait for modal to appear
modal = SmartLocator("role=dialog", adapter, "Modal dialog")
modal.wait_visible(timeout=5)

# Check if modal is open
if modal.is_visible():
    print("Modal is open")

# Interact with modal content
modal_title = SmartLocator("role=dialog >> h2", adapter, "Modal title")
title_text = modal_title.text()

# Close modal (via Escape key)
modal.press_key("Escape")

# Or close via button
close_btn = SmartLocator("role=dialog >> button[aria-label='Close']", adapter)
close_btn.click()

# Wait for modal to disappear
modal.wait_hidden(timeout=5)
```

#### Drawers / Sidebars
```python
# Open drawer
menu_btn = SmartLocator("button[aria-label='Menu']", adapter, "Menu button")
menu_btn.click()

drawer = SmartLocator("[role='navigation'].drawer", adapter, "Sidebar drawer")
drawer.wait_visible()

# Navigate in drawer
profile_link = SmartLocator(".drawer a[href='/profile']", adapter, "Profile")
profile_link.click()
```

#### Cards
```python
# Click card
product_card = SmartLocator(".product-card:first-child", adapter, "First product")
product_card.click()

# Get card title
card_title = SmartLocator(".product-card h3", adapter, "Product title")
title = card_title.text()

# Hover over card
product_card.hover()
```

#### Panels / Sections
```python
# Collapsible panel
panel_header = SmartLocator(".panel-header", adapter, "Panel header")
panel_header.click()

# Check if panel is expanded
panel = SmartLocator(".panel", adapter, "Panel")
is_expanded = panel.get_attribute("aria-expanded") == "true"
```

#### Overlays
```python
# Loading overlay
overlay = SmartLocator(".loading-overlay", adapter, "Loading overlay")
overlay.wait_hidden(timeout=30)  # Wait for loading to finish
```

---

### 4. **Data Display & Interactive Widgets**

#### Tables (Static)
```python
# Get all table data
table = SmartLocator("table#users", adapter, "Users table")

# Via adapter (for complex table operations)
from core.smart_locator import PlaywrightAdapter

adapter = PlaywrightAdapter(page)

# Get all table data as 2D array
all_data = adapter.get_table_data("table#users")
print(f"Total rows: {len(all_data)}")

# Get specific row
row_2 = adapter.get_table_row("table#users", 1)  # 0-indexed
print(f"Row 2: {row_2}")

# Get specific cell
cell_value = adapter.get_table_cell("table#users", 1, 2)  # Row 1, Col 2
print(f"Cell: {cell_value}")

# Click table row
row = SmartLocator("table#users tr:nth-child(2)", adapter, "Second row")
row.click()

# Sort table column
sort_btn = SmartLocator("table#users th:nth-child(1)", adapter, "Name column header")
sort_btn.click()
```

#### Tables (Paginated)
```python
# Navigate pages
next_btn = SmartLocator("button[aria-label='Next page']", adapter, "Next page")
next_btn.click()

prev_btn = SmartLocator("button[aria-label='Previous page']", adapter, "Previous")
prev_btn.click()

# Select page size
page_size = SmartLocator("select[name='pageSize']", adapter, "Page size")
page_size.select_option("50", by="value")
```

#### Tables (Sortable/Filterable)
```python
# Sort by column
name_header = SmartLocator("th[data-column='name']", adapter, "Name column")
name_header.click()  # Sort ascending
name_header.click()  # Sort descending

# Filter table
filter_input = SmartLocator("input[placeholder='Filter']", adapter, "Filter")
filter_input.fill("John")

# Wait for filtered results
table.wait_visible()
```

#### Trees / Hierarchical Lists
```python
# Expand tree node
node = SmartLocator("role=treeitem[name='Documents']", adapter, "Documents node")
node.click()

# Check if expanded
is_expanded = node.get_attribute("aria-expanded") == "true"

# Select child node
child = SmartLocator("role=treeitem[name='Reports']", adapter, "Reports")
child.click()
```

#### Charts (Canvas / SVG)
```python
# Click chart element
chart_bar = SmartLocator("svg rect[data-value='2023']", adapter, "2023 data point")
chart_bar.click()

# Hover for tooltip
chart_bar.hover()

# Get chart legend
legend_item = SmartLocator(".chart-legend-item:first-child", adapter, "Legend")
legend_text = legend_item.text()
```

#### Maps (Leaflet/Mapbox)
```python
# Click map marker
marker = SmartLocator(".leaflet-marker-icon[alt='Store 1']", adapter, "Store 1")
marker.click()

# Zoom in
zoom_in = SmartLocator(".leaflet-control-zoom-in", adapter, "Zoom in")
zoom_in.click()

# Hover over region
region = SmartLocator("path[data-region='CA']", adapter, "California")
region.hover()
```

---

### 5. **Dynamic / Rich UI**

#### Autocomplete / Typeahead
```python
# Type in autocomplete
search_input = SmartLocator("input[role='combobox']", adapter, "Search box")
search_input.fill("New Y")

# Wait for suggestions
suggestions = SmartLocator("role=listbox", adapter, "Suggestions")
suggestions.wait_visible()

# Select suggestion
option = SmartLocator("role=option[name='New York']", adapter, "New York option")
option.click()

# Or navigate with keyboard
search_input.press_key("ArrowDown")
search_input.press_key("ArrowDown")
search_input.press_key("Enter")
```

#### Dropdowns (Custom/Rich)
```python
# Open dropdown
dropdown_btn = SmartLocator("button[aria-haspopup='listbox']", adapter, "Dropdown")
dropdown_btn.click()

# Wait for dropdown menu
menu = SmartLocator("role=listbox", adapter, "Dropdown menu")
menu.wait_visible()

# Select option
option = SmartLocator("role=option[name='Option 2']", adapter, "Option 2")
option.click()
```

#### Multi-Select Lists / Chips
```python
# Add item to multi-select
multi_select = SmartLocator(".multi-select", adapter, "Multi-select")
multi_select.click()

option = SmartLocator("role=option[name='Tag 1']", adapter, "Tag 1")
option.click()

# Remove chip
chip = SmartLocator(".chip:first-child button", adapter, "Remove first chip")
chip.click()

# Get all selected items
selected_chips = SmartLocator(".chip", adapter, "Chips")
count = selected_chips.count()
print(f"Selected: {count} items")
```

#### Tokenizers
```python
# Add token
input_field = SmartLocator(".tokenizer-input", adapter, "Tokenizer input")
input_field.fill("Python")
input_field.press_key("Enter")

input_field.fill("JavaScript")
input_field.press_key("Enter")

# Remove token
token = SmartLocator(".token button[aria-label='Remove']", adapter, "Remove token")
token.click()
```

#### Date Picker / Calendar
```python
# Open date picker
date_input = SmartLocator("input[type='date']", adapter, "Date picker")
date_input.click()

# Or click calendar icon
calendar_icon = SmartLocator("button[aria-label='Choose date']", adapter)
calendar_icon.click()

# Select date
date_cell = SmartLocator("button[data-date='2025-12-25']", adapter, "Dec 25")
date_cell.click()

# Navigate months
next_month = SmartLocator("button[aria-label='Next month']", adapter)
next_month.click()

# Select today
today_btn = SmartLocator("button.today", adapter, "Today button")
today_btn.click()
```

#### Time Picker
```python
# Open time picker
time_input = SmartLocator("input[type='time']", adapter, "Time picker")
time_input.click()

# Select hour
hour = SmartLocator("button[data-hour='14']", adapter, "2 PM")
hour.click()

# Select minute
minute = SmartLocator("button[data-minute='30']", adapter, "30 minutes")
minute.click()
```

#### Carousels / Sliders / Galleries
```python
# Navigate carousel
next_btn = SmartLocator(".carousel-next", adapter, "Next slide")
next_btn.click()

prev_btn = SmartLocator(".carousel-prev", adapter, "Previous slide")
prev_btn.click()

# Click specific slide
slide = SmartLocator(".carousel-slide:nth-child(3)", adapter, "Slide 3")
slide.click()

# Click thumbnail
thumbnail = SmartLocator(".carousel-thumbnail:nth-child(2)", adapter, "Thumb 2")
thumbnail.click()
```

#### Tooltips
```python
# Hover to show tooltip
button = SmartLocator("button#info", adapter, "Info button")
button.hover()

# Wait for tooltip
tooltip = SmartLocator("role=tooltip", adapter, "Tooltip")
tooltip.wait_visible()

# Get tooltip text
tooltip_text = tooltip.text()
print(f"Tooltip: {tooltip_text}")
```

#### Popovers
```python
# Click to show popover
trigger = SmartLocator("button#show-popover", adapter, "Show popover")
trigger.click()

# Wait for popover
popover = SmartLocator("role=dialog", adapter, "Popover")
popover.wait_visible()

# Interact with popover content
confirm_btn = SmartLocator("role=dialog >> button", adapter, "Confirm")
confirm_btn.click()
```

#### Toast / Snackbar Notifications
```python
# Wait for toast notification
toast = SmartLocator(".toast, .snackbar, role=alert", adapter, "Toast notification")
toast.wait_visible(timeout=5)

# Get toast message
message = toast.text()
print(f"Notification: {message}")

# Close toast
close_btn = SmartLocator(".toast button[aria-label='Close']", adapter)
if close_btn.is_visible():
    close_btn.click()

# Wait for toast to disappear
toast.wait_hidden(timeout=10)
```

#### Virtualized Lists (Infinite Scroll)
```python
# Scroll to load more items
list_container = SmartLocator(".virtualized-list", adapter, "List container")

# Scroll to bottom
list_container.scroll_into_view()

# Wait for new items to load
import time
time.sleep(1)

# Get item count
items = SmartLocator(".list-item", adapter, "List items")
count = items.count()
print(f"Loaded {count} items")

# Scroll specific item into view
item_100 = SmartLocator(".list-item[data-index='100']", adapter, "Item 100")
item_100.scroll_into_view()
```

---

### 6. **Accessibility / Semantic Elements (ARIA Roles)**

#### ARIA Dialog
```python
# Modal dialog
dialog = SmartLocator("role=dialog", adapter, "Dialog")
dialog.wait_visible()

# Get dialog title
title = SmartLocator("role=dialog >> [role=heading]", adapter, "Dialog title")
title_text = title.text()

# Close dialog
close_btn = SmartLocator("role=dialog >> button[aria-label='Close']", adapter)
close_btn.click()
```

#### ARIA Alert
```python
# Wait for alert
alert = SmartLocator("role=alert", adapter, "Alert")
alert.wait_visible()

# Get alert message
message = alert.text()
print(f"Alert: {message}")
```

#### ARIA Combobox
```python
# Autocomplete/search box
combobox = SmartLocator("role=combobox", adapter, "Search combobox")
combobox.fill("query")

# Wait for dropdown
listbox = SmartLocator("role=listbox", adapter, "Suggestions")
listbox.wait_visible()

# Select option
option = SmartLocator("role=option", adapter, "First option")
option.click()
```

#### ARIA Menu
```python
# Open menu
menu_btn = SmartLocator("role=button[aria-haspopup=menu]", adapter, "Menu button")
menu_btn.click()

# Select menu item
menu_item = SmartLocator("role=menuitem[name='Settings']", adapter, "Settings")
menu_item.click()
```

#### ARIA Listbox
```python
# Select from listbox
listbox = SmartLocator("role=listbox", adapter, "Options list")
option = SmartLocator("role=option[name='Option 1']", adapter, "Option 1")
option.click()

# Multi-select listbox
option_2 = SmartLocator("role=option[name='Option 2']", adapter, "Option 2")
option_2.click()  # Hold Ctrl for multi-select
```

#### ARIA Tree
```python
# Hierarchical tree
tree = SmartLocator("role=tree", adapter, "File tree")

# Expand tree item
item = SmartLocator("role=treeitem[name='Documents']", adapter, "Documents")
item.click()

# Select nested item
nested = SmartLocator("role=treeitem[name='Reports']", adapter, "Reports")
nested.click()
```

#### ARIA Grid (Data Grid)
```python
# Interactive data grid
grid = SmartLocator("role=grid", adapter, "Data grid")

# Click grid cell
cell = SmartLocator("role=gridcell", adapter, "Cell")
cell.click()

# Edit cell
cell.double_click()
cell.fill("New value")
cell.press_key("Enter")
```

#### ARIA Tab Panel
```python
# Select tab
tab = SmartLocator("role=tab[name='Profile']", adapter, "Profile tab")
tab.click()

# Wait for tab panel
panel = SmartLocator("role=tabpanel[aria-labelledby='profile']", adapter)
panel.wait_visible()
```

---

## 🚀 Advanced Interactions

### Hover Interactions
```python
# Hover to reveal dropdown
menu = SmartLocator(".nav-item", adapter, "Nav item")
menu.hover()

dropdown = SmartLocator(".dropdown-menu", adapter, "Dropdown menu")
dropdown.wait_visible()

# Hover to show tooltip
info_icon = SmartLocator(".info-icon", adapter, "Info icon")
info_icon.hover()

tooltip = SmartLocator("role=tooltip", adapter, "Tooltip")
print(tooltip.text())
```

### Keyboard Navigation
```python
# Navigate with arrow keys
list_item = SmartLocator("role=listbox", adapter, "List")
list_item.press_key("ArrowDown")
list_item.press_key("ArrowDown")
list_item.press_key("Enter")

# Tab navigation
input_field = SmartLocator("input#first", adapter, "First field")
input_field.fill("value1")
input_field.press_key("Tab")

# Next field gets focus automatically
```

### Drag and Drop
```python
# Drag item to target
source = SmartLocator(".draggable-item", adapter, "Draggable item")
target = SmartLocator(".drop-zone", adapter, "Drop zone")

source.drag_to(target.get_current_locator())

# Or reorder list items
item_1 = SmartLocator(".list-item:nth-child(1)", adapter, "Item 1")
item_3 = SmartLocator(".list-item:nth-child(3)", adapter, "Item 3")

item_1.drag_to(item_3.get_current_locator())
```

### Scroll Operations
```python
# Scroll element into view
footer = SmartLocator("footer", adapter, "Footer")
footer.scroll_into_view()

# Scroll to lazy-load content
container = SmartLocator(".infinite-scroll", adapter, "Scroll container")
container.scroll_into_view()

# Wait for content to load
import time
time.sleep(1)
```

### Wait Operations
```python
# Wait for element to appear
loading = SmartLocator(".loading-spinner", adapter, "Loading spinner")
button = SmartLocator("button#submit", adapter, "Submit button")

# Wait for loading to finish
loading.wait_hidden(timeout=30)

# Then click button
button.wait_visible(timeout=10)
button.click()

# Wait for success message
success = SmartLocator(".success-message", adapter, "Success")
success.wait_visible(timeout=5)
```

### Attribute & Property Checks
```python
# Check disabled state
submit_btn = SmartLocator("button#submit", adapter, "Submit button")
is_disabled = not submit_btn.is_enabled()

# Check aria attributes
tab = SmartLocator("role=tab", adapter, "Tab")
is_selected = tab.get_attribute("aria-selected") == "true"

# Check data attributes
item = SmartLocator(".item", adapter, "Item")
item_id = item.get_attribute("data-id")

# Check CSS classes
has_error = "error" in (item.get_attribute("class") or "")
```

### Multi-Element Operations
```python
# Count elements
items = SmartLocator(".product-card", adapter, "Product cards")
total = items.count()
print(f"Found {total} products")

# Iterate over elements (via adapter)
for i in range(total):
    card = SmartLocator(f".product-card:nth-child({i+1})", adapter, f"Product {i+1}")
    name = card.text()
    print(f"Product {i+1}: {name}")
```

---

## 🎓 Best Practices

### 1. Use Context Hints
```python
# Good: Helps AI understand element purpose
submit = SmartLocator("button#submit", adapter, "Submit login form button")

# Better: More context for healing
primary_btn = SmartLocator(".btn-primary", adapter, 
    "Primary submit button in login form (blue button at bottom)")
```

### 2. Wait for Dynamic Elements
```python
# Always wait for dynamic content
modal = SmartLocator("role=dialog", adapter, "Modal")
modal.wait_visible(timeout=10)

# Then interact
modal_input = SmartLocator("role=dialog >> input", adapter, "Modal input")
modal_input.fill("value")
```

### 3. Use ARIA Roles When Available
```python
# Prefer semantic locators
# Good
dialog = SmartLocator("role=dialog", adapter, "Dialog")
menu = SmartLocator("role=menu", adapter, "Menu")

# Instead of
dialog = SmartLocator(".modal-dialog", adapter, "Dialog")
menu = SmartLocator(".dropdown-menu", adapter, "Menu")
```

### 4. Handle Hover-Dependent UI
```python
# Hover first, then interact
dropdown = SmartLocator(".nav-item", adapter, "Nav item")
dropdown.hover()

# Wait for submenu
submenu = SmartLocator(".submenu", adapter, "Submenu")
submenu.wait_visible()

# Then click item
item = SmartLocator(".submenu-item:first-child", adapter, "First item")
item.click()
```

### 5. Combine Multiple Strategies
```python
# Try multiple approaches
try:
    # Try by ID first
    submit = SmartLocator("#submit-btn", adapter, "Submit button")
    submit.click()
except:
    # Fall back to role
    submit = SmartLocator("role=button[name='Submit']", adapter, "Submit")
    submit.click()

# Or let AI healing handle it automatically!
submit = SmartLocator("#submit-btn", adapter, "Submit button")
submit.click()  # Auto-heals to working locator if ID changes
```

---

## ✅ Complete Feature Matrix

| Feature | Playwright | Selenium | Auto-Healing |
|---------|------------|----------|--------------|
| **Form Controls** | ✅ | ✅ | ✅ |
| Text Inputs | ✅ | ✅ | ✅ |
| Checkboxes | ✅ | ✅ | ✅ |
| Radio Buttons | ✅ | ✅ | ✅ |
| Dropdowns | ✅ | ✅ | ✅ |
| File Upload | ✅ | ✅ | ✅ |
| **Actions** | ✅ | ✅ | ✅ |
| Click | ✅ | ✅ | ✅ |
| Double-Click | ✅ | ✅ | ✅ |
| Right-Click | ✅ | ✅ | ✅ |
| Hover | ✅ | ✅ | ✅ |
| Drag & Drop | ✅ | ✅ | ✅ |
| Keyboard | ✅ | ✅ | ✅ |
| **Visibility** | ✅ | ✅ | ✅ |
| Wait Visible | ✅ | ✅ | ✅ |
| Wait Hidden | ✅ | ✅ | ✅ |
| Scroll Into View | ✅ | ✅ | ✅ |
| **Containers** | ✅ | ✅ | ✅ |
| Modals | ✅ | ✅ | ✅ |
| Dialogs | ✅ | ✅ | ✅ |
| Tooltips | ✅ | ✅ | ✅ |
| Popovers | ✅ | ✅ | ✅ |
| **Data Display** | ✅ | ✅ | ✅ |
| Tables | ✅ | ✅ | ✅ |
| Trees | ✅ | ✅ | ✅ |
| Charts | ✅ | ✅ | ✅ |
| **ARIA Roles** | ✅ | ✅ | ✅ |
| All ARIA elements | ✅ | ✅ | ✅ |

---

## 📚 Related Documentation

- **Locator Types**: `docs/LOCATOR_TYPES_GUIDE.md`
- **REST API**: `docs/API_QUICK_START.md`
- **Architecture**: `docs/MICROSERVICES_ARCHITECTURE.md`

---

**Framework Enhanced by: Ram, Senior AI Test Automation Engineer** 🚀

**All UI element types now supported with AI-powered auto-healing!**
