"""
Smart Locator - Cross-Framework POM Layer
==========================================

Universal Page Object Model layer that works with:
- Playwright
- Selenium
- Any framework through adapters

Features:
- Auto-healing locators (powered by AI microservice)
- Framework-agnostic API
- Intelligent retry logic
- Detailed logging
"""

from .smart_locator import SmartLocator
from .smart_page import SmartPage
from .framework_adapter import FrameworkAdapter, PlaywrightAdapter, SeleniumAdapter

__all__ = [
    'SmartLocator',
    'SmartPage',
    'FrameworkAdapter',
    'PlaywrightAdapter',
    'SeleniumAdapter'
]
