# 🎯 SmartLocator - Universal Locator Support Guide

## Overview

**SmartLocator** now supports **ALL major locator types** for both Playwright and Selenium frameworks with AI-powered auto-healing!

---

## ✨ Key Features

- ✅ **Universal Support**: Works with ANY locator type
- ✅ **Auto-Healing**: AI repairs broken locators automatically
- ✅ **Framework-Agnostic**: Same API for Playwright and Selenium
- ✅ **Intelligent Detection**: Auto-detects locator type
- ✅ **Explicit Prefixes**: Use prefixes for clarity (optional)

---

## 🎭 Playwright Locator Types

### 1. CSS Selector (Default)
```python
# ID
SmartLocator("button#submit", adapter)
SmartLocator("#submit", adapter)

# Class
SmartLocator(".btn-primary", adapter)
SmartLocator("button.btn-primary", adapter)

# Attribute
SmartLocator("input[name='username']", adapter)
SmartLocator("[data-testid='login-btn']", adapter)

# Descendant
SmartLocator("form > button", adapter)
SmartLocator("div.container button", adapter)
```

### 2. XPath
```python
# Standard XPath
SmartLocator("//button[@id='submit']", adapter)
SmartLocator("//input[@name='username']", adapter)

# XPath with text
SmartLocator("//button[text()='Submit']", adapter)
SmartLocator("//a[contains(text(), 'Click')]", adapter)

# Explicit prefix
SmartLocator("xpath=//button[@id='submit']", adapter)
```

### 3. Text Content
```python
# Exact text match
SmartLocator("text='Click Here'", adapter)
SmartLocator("text='Submit Form'", adapter)

# Partial text match
SmartLocator("text=Click", adapter)
SmartLocator("text=Submit", adapter)
```

### 4. ARIA Role
```python
# Role with name
SmartLocator("role=button[name='Submit']", adapter)
SmartLocator("role=textbox[name='Username']", adapter)

# Role only
SmartLocator("role=button", adapter)
SmartLocator("role=link", adapter)
```

### 5. Test ID
```python
# Data-testid attribute
SmartLocator("[data-testid='login-btn']", adapter)
SmartLocator("data-testid=login-btn", adapter)

# Custom test attribute
SmartLocator("[data-test='submit']", adapter)
```

### 6. Label (Form inputs)
```python
# Find input by label
SmartLocator("label=Username", adapter)
SmartLocator("label='Email Address'", adapter)
```

### 7. Placeholder
```python
# Find input by placeholder
SmartLocator("placeholder='Enter name'", adapter)
SmartLocator("placeholder=Search", adapter)
```

### 8. Alt Text (Images)
```python
# Find image by alt text
SmartLocator("alt='Company Logo'", adapter)
SmartLocator("alt=Profile", adapter)
```

### 9. Title Attribute
```python
# Find by title
SmartLocator("title='Submit form'", adapter)
SmartLocator("title=Close", adapter)
```

---

## 🔧 Selenium Locator Types

### 1. CSS Selector (Default)
```python
# ID
SmartLocator("button#submit", adapter)
SmartLocator("#login-btn", adapter)

# Class
SmartLocator(".btn-primary", adapter)
SmartLocator("button.btn-danger", adapter)

# Attribute
SmartLocator("input[name='username']", adapter)
SmartLocator("[data-testid='submit']", adapter)

# Complex
SmartLocator("form > div.form-group > input", adapter)
```

### 2. XPath
```python
# Standard XPath
SmartLocator("//button[@id='submit']", adapter)
SmartLocator("//input[@name='username']", adapter)

# XPath with text
SmartLocator("//button[text()='Submit']", adapter)
SmartLocator("//a[contains(text(), 'Click')]", adapter)

# Explicit prefix
SmartLocator("xpath=//button[@id='submit']", adapter)
```

### 3. ID (Explicit)
```python
# Using prefix
SmartLocator("id=submit", adapter)
SmartLocator("id=login-btn", adapter)

# Auto-detect (single #)
SmartLocator("#submit", adapter)  # ← Auto-detects as ID if simple
```

### 4. Name Attribute
```python
SmartLocator("name=username", adapter)
SmartLocator("name=email", adapter)
SmartLocator("name=password", adapter)
```

### 5. Class Name (Single class)
```python
# Using prefix
SmartLocator("class=btn-primary", adapter)
SmartLocator("classname=btn-danger", adapter)

# Auto-detect (single .)
SmartLocator(".btn-primary", adapter)  # ← Auto-detects if simple
```

### 6. Tag Name
```python
SmartLocator("tag=button", adapter)
SmartLocator("tagname=input", adapter)
SmartLocator("tag=a", adapter)
```

### 7. Link Text (Exact match)
```python
SmartLocator("link=Click Here", adapter)
SmartLocator("linktext=Sign Up", adapter)
SmartLocator("link_text=Login", adapter)
```

### 8. Partial Link Text
```python
SmartLocator("partial_link=Click", adapter)
SmartLocator("partiallink=Sign", adapter)
SmartLocator("partial=Log", adapter)
```

---

## 📚 Usage Examples

### Example 1: Multiple Locator Strategies
```python
from core.smart_locator import SmartLocator, PlaywrightAdapter

adapter = PlaywrightAdapter(page)

# Try CSS first, falls back to text if broken
submit_btn = SmartLocator("button#submit", adapter, context_hint="Submit button")
submit_btn.click()  # Auto-heals to "text=Submit" if ID changes

# Try role first, falls back to CSS if broken
search_input = SmartLocator("role=textbox[name='Search']", adapter, context_hint="Search box")
search_input.fill("test query")  # Auto-heals to CSS if role changes
```

### Example 2: Selenium with Different Strategies
```python
from core.smart_locator import SmartLocator, SeleniumAdapter

adapter = SeleniumAdapter(driver)

# ID strategy
username = SmartLocator("id=username", adapter)
username.fill("john@example.com")

# XPath strategy
password = SmartLocator("//input[@type='password']", adapter)
password.fill("secret123")

# Link text strategy
signup_link = SmartLocator("link=Sign Up", adapter)
signup_link.click()

# CSS strategy (default)
submit = SmartLocator("button.btn-submit", adapter)
submit.click()
```

### Example 3: Auto-Detection
```python
# SmartLocator automatically detects locator type!

# Detects XPath (starts with //)
SmartLocator("//button[@id='submit']", adapter)

# Detects CSS (default)
SmartLocator("button#submit", adapter)

# Detects ID (starts with # and simple)
SmartLocator("#submit", adapter)

# Detects text (Playwright-specific)
SmartLocator("text=Click Here", adapter)

# Detects role (Playwright-specific)
SmartLocator("role=button[name='Submit']", adapter)
```

### Example 4: Explicit Prefixes (Recommended for Clarity)
```python
# Explicit is better than implicit!

# Selenium
SmartLocator("id=submit", adapter)           # Clear: Using ID
SmartLocator("name=username", adapter)       # Clear: Using name
SmartLocator("xpath=//button", adapter)      # Clear: Using XPath
SmartLocator("class=btn-primary", adapter)   # Clear: Using class
SmartLocator("link=Sign Up", adapter)        # Clear: Using link text

# Playwright (native syntax)
SmartLocator("text=Click Here", adapter)     # Clear: Using text
SmartLocator("role=button", adapter)         # Clear: Using role
```

### Example 5: With SmartPage
```python
from core.smart_locator import SmartPage, PlaywrightAdapter

class LoginPage(SmartPage):
    def __init__(self, adapter):
        super().__init__(adapter)
        
        # Different locator strategies
        self.username_input = self.locator("id=username", "Username field")
        self.password_input = self.locator("name=password", "Password field")
        self.submit_btn = self.locator("text=Login", "Login button")
        self.signup_link = self.locator("role=link[name='Sign Up']", "Signup link")
    
    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_btn.click()
```

---

## 🔄 Auto-Healing Examples

### Scenario 1: ID Changed
```python
# Original locator: button#submit-btn
locator = SmartLocator("button#submit-btn", adapter, context_hint="Submit button")

# Developer changed ID to #submit-form-btn
locator.click()
# ⚠️  Locator failed: button#submit-btn
# 🔧 Attempting AI-powered repair...
# ✅ AI suggested: button#submit-form-btn
# ✅ Healed locator working: button#submit-form-btn
```

### Scenario 2: Class Changed
```python
# Original: .btn-primary
locator = SmartLocator(".btn-primary", adapter, context_hint="Primary button")

# Developer changed to .btn-success
locator.click()
# ⚠️  Locator failed: .btn-primary
# 🔧 Attempting AI-powered repair...
# ✅ AI suggested: .btn-success
```

### Scenario 3: XPath Changed
```python
# Original: //div[@id='container']/button
locator = SmartLocator("//div[@id='container']/button", adapter, context_hint="Submit")

# DOM structure changed
locator.click()
# ⚠️  Locator failed: //div[@id='container']/button
# 🔧 Attempting AI-powered repair...
# ✅ AI suggested: //section[@class='form']/button[@type='submit']
```

---

## 🎯 Locator Strategy Recommendations

### Playwright Best Practices
1. **Prefer semantic locators** (role, label, text)
   - `role=button[name='Submit']` ← Best
   - `text=Submit` ← Good
   - `#submit-btn` ← OK
   - `xpath=//div[3]/button[2]` ← Avoid (brittle)

2. **Use test IDs for dynamic content**
   - `[data-testid='user-profile']`

3. **Combine strategies for robustness**
   - Start specific, AI heals to alternatives

### Selenium Best Practices
1. **Priority order**:
   - ID (`id=submit`) ← Best (unique, fast)
   - Name (`name=username`) ← Good
   - CSS (`button.btn-primary`) ← Good
   - Link text (`link=Click Here`) ← Good for links
   - XPath (`//button[@id='submit']`) ← Last resort

2. **Avoid brittle XPaths**:
   - ❌ `//div[3]/div[2]/button[1]` (breaks easily)
   - ✅ `//button[@id='submit']` (semantic)

---

## 🔍 Locator Type Detection Logic

### Playwright
```
1. If starts with "text=", "role=", "label=", etc. → Use Playwright syntax
2. If starts with "//" → XPath
3. Otherwise → CSS selector (Playwright handles all CSS)
```

### Selenium
```
1. If contains "=" and not XPath → Parse prefix (id=, name=, etc.)
2. If starts with "//" → XPath
3. If starts with "#" (simple) → ID
4. If starts with "." (simple) → Class
5. Otherwise → CSS selector
```

---

## 📊 Comparison Matrix

| Locator Type | Playwright | Selenium | Speed | Robustness | Readability |
|--------------|------------|----------|-------|------------|-------------|
| **ID** | ✅ `#id` | ✅ `id=id` | ⚡ Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **CSS** | ✅ Native | ✅ Default | ⚡ Fast | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **XPath** | ✅ Native | ✅ Native | 🐢 Slow | ⭐⭐⭐ | ⭐⭐ |
| **Text** | ✅ `text=` | ❌ - | ⚡ Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Role** | ✅ `role=` | ❌ - | ⚡ Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Name** | ✅ CSS | ✅ `name=` | ⚡ Fast | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Class** | ✅ `.class` | ✅ `class=` | ⚡ Fast | ⭐⭐⭐ | ⭐⭐⭐ |
| **Link Text** | ✅ `text=` | ✅ `link=` | ⚡ Fast | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Test ID** | ✅ `[data-testid]` | ✅ CSS | ⚡ Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Legend**:
- ⚡ Fast: <10ms
- 🐢 Slow: 10-50ms
- ⭐⭐⭐⭐⭐ Excellent
- ⭐⭐⭐⭐ Good
- ⭐⭐⭐ Fair
- ⭐⭐ Poor

---

## 🚀 Quick Reference

### Playwright Syntax
```python
"button#id"                      # CSS selector
"//button[@id='submit']"         # XPath
"text=Click Here"                # Text content
"text='Exact Match'"             # Exact text
"role=button[name='Submit']"     # ARIA role
"[data-testid='login']"          # Test ID
"label=Username"                 # Form label
"placeholder=Search"             # Placeholder
"alt=Logo"                       # Alt text
"title=Close"                    # Title
```

### Selenium Syntax
```python
"button#id"                      # CSS selector (default)
"//button[@id='submit']"         # XPath
"id=submit"                      # ID (explicit)
"name=username"                  # Name attribute
"class=btn-primary"              # Class name
"tag=button"                     # Tag name
"link=Click Here"                # Link text (exact)
"partial_link=Click"             # Partial link text
"xpath=//button"                 # XPath (explicit)
"css=button#id"                  # CSS (explicit)
```

---

## 🎓 Advanced Tips

### 1. Combine Context Hints with Locators
```python
# Good: Helps AI understand element purpose
SmartLocator("button#submit", adapter, context_hint="Submit button on login form")

# Better: AI knows what to look for if locator breaks
SmartLocator(".btn-primary", adapter, context_hint="Primary submit button (blue)")
```

### 2. Use Multiple Strategies in Sequence
```python
# Try specific first, fallback to general
primary_locators = [
    "role=button[name='Submit']",  # Most semantic
    "button#submit-btn",            # Specific ID
    "button.btn-submit",            # Class-based
    "text=Submit"                   # Fallback to text
]

# SmartLocator will AI-heal to any of these if original breaks!
```

### 3. Test Your Locators
```python
from core.smart_locator import SmartLocator

# Test visibility
locator = SmartLocator("button#submit", adapter)
if locator.is_visible():
    print("✅ Element found and visible")
    
# Get current working locator
print(f"Current locator: {locator.get_current_locator()}")
print(f"Was healed: {locator.was_healed()}")
```

---

## 📖 Related Documentation

- **SmartLocator API**: See `core/smart_locator/smart_locator.py`
- **Framework Adapters**: See `core/smart_locator/framework_adapter.py`
- **SmartPage Guide**: See `docs/IMPLEMENTATION_SUMMARY.md`
- **REST API**: See `docs/API_QUICK_START.md`

---

## ✅ Summary

SmartLocator now supports **ALL major locator types**:

### Playwright: 10+ locator types
- ✅ CSS, XPath, Text, Role, Test ID, Label, Placeholder, Alt, Title, and more

### Selenium: 8+ locator types
- ✅ CSS, XPath, ID, Name, Class, Tag, Link Text, Partial Link Text

### Key Benefits
- 🎯 **Universal**: One API, all locator types
- 🔄 **Auto-Healing**: AI repairs broken locators
- 🚀 **Smart Detection**: Auto-detects locator type
- 📝 **Explicit Prefixes**: Optional for clarity

---

**Happy Testing! 🚀**
