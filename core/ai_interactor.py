"""
AIInteractor - Adaptive Interaction Layer
==========================================

Universal interaction engine that attempts actions in fallback hierarchy:
1. Direct framework action (page.fill / page.click)
2. JS injection (set value + dispatch events)
3. Simulated human typing (character-by-character with delays)
4. Degraded mode (log failure)

Author: Ram
Date: November 12, 2025
Phase: 7 - Universal Interactor
"""

from typing import Optional, Dict, Any
import time
import logging
import random

try:
    from playwright.sync_api import Page, TimeoutError as PWTimeoutError
except ImportError:
    # Fallback for type hints
    Page = Any
    PWTimeoutError = Exception

log = logging.getLogger(__name__)


class AIInteractor:
    """
    Adaptive interactor that handles anti-automation protection.
    
    Attempts actions in order:
    1. Direct framework action (page.fill / page.click)
    2. JS injection (set value + dispatch input events)
    3. Simulated human typing (character-by-character)
    4. Degraded mode (returns False, logs failure)
    
    Usage:
        interactor = AIInteractor(page, timeout=5000)
        success = interactor.safe_fill("#username", "myuser")
        if success:
            print("Field filled successfully")
    """
    
    def __init__(self, page: Page, timeout: float = 5000):
        """
        Initialize AIInteractor.
        
        Args:
            page: Playwright Page object
            timeout: Timeout in milliseconds for each attempt (default: 5000ms)
        """
        self.page = page
        self.timeout = timeout / 1000.0  # Convert to seconds
        self.interaction_log: list = []
        
    def safe_fill(self, selector: str, value: str, context_hint: str = "") -> bool:
        """
        Safely fill a form field using adaptive fallback strategies.
        
        Args:
            selector: CSS selector for the input field
            value: Value to fill
            context_hint: Optional context for logging (e.g., "username field")
            
        Returns:
            bool: True if any method succeeded, False if all failed
            
        Example:
            >>> interactor = AIInteractor(page)
            >>> success = interactor.safe_fill("#username", "testuser")
            >>> print(f"Fill succeeded: {success}")
        """
        start = time.perf_counter()
        log.info(f"[AIInteractor] safe_fill selector={selector} context={context_hint}")
        
        # 1) Try native fill
        try:
            timeout_ms = int(self.timeout * 1000)
            self.page.fill(selector, value, timeout=timeout_ms)
            log.info("[AIInteractor] ✅ fill via DIRECT method succeeded")
            self._log_method('direct', start, selector, context_hint)
            return True
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ native fill failed: {e}")
        
        # 2) Try JS injection
        try:
            result = self.page.evaluate(
                """(sel, val) => {
                    const el = document.querySelector(sel);
                    if (!el) return false;
                    el.focus();
                    el.value = val;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                    return true;
                }""",
                selector,
                value,
            )
            if result:
                log.info("[AIInteractor] ✅ fill via JS_INJECT method succeeded")
                self._log_method('js_inject', start, selector, context_hint)
                return True
            else:
                log.warning(f"[AIInteractor] ⚠️ JS injection returned false (element not found)")
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ JS injection failed: {e}")
        
        # 3) Human-like typing - fallback slow but effective
        try:
            # First, try to focus the field
            self.page.focus(selector, timeout=int(self.timeout * 1000))
            
            # Try to clear with keyboard (select all + delete)
            try:
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")
            except:
                pass  # If clear fails, typing will overwrite
            
            # Type character by character with random delays
            for ch in value:
                delay = random.randint(45, 80)  # Random delay 45-80ms
                self.page.type(selector, ch, delay=delay)
            
            log.info("[AIInteractor] ✅ fill via HUMAN_TYPING method succeeded")
            self._log_method('human_typing', start, selector, context_hint)
            return True
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ human typing failed: {e}")
        
        # 4) All methods failed - degraded mode
        log.error(f"[AIInteractor] ❌ All fill methods FAILED for selector={selector}")
        self._log_method('degraded', start, selector, context_hint, failed=True)
        return False
    
    def safe_click(self, selector: str, context_hint: str = "") -> bool:
        """
        Safely click an element using adaptive fallback strategies.
        
        Args:
            selector: CSS selector for the clickable element
            context_hint: Optional context for logging (e.g., "login button")
            
        Returns:
            bool: True if any method succeeded, False if all failed
            
        Example:
            >>> interactor = AIInteractor(page)
            >>> success = interactor.safe_click("button[type='submit']")
            >>> print(f"Click succeeded: {success}")
        """
        start = time.perf_counter()
        log.info(f"[AIInteractor] safe_click selector={selector} context={context_hint}")
        
        # 1) Try native click
        try:
            timeout_ms = int(self.timeout * 1000)
            self.page.click(selector, timeout=timeout_ms)
            log.info("[AIInteractor] ✅ click via DIRECT method succeeded")
            self._log_method('direct', start, selector, context_hint)
            return True
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ native click failed: {e}")
        
        # 2) Try JS click
        try:
            result = self.page.evaluate(
                """(sel) => {
                    const el = document.querySelector(sel);
                    if (!el) return false;
                    el.click();
                    return true;
                }""",
                selector,
            )
            if result:
                log.info("[AIInteractor] ✅ click via JS_INJECT method succeeded")
                self._log_method('js_inject', start, selector, context_hint)
                return True
            else:
                log.warning(f"[AIInteractor] ⚠️ JS click returned false (element not found)")
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ JS click failed: {e}")
        
        # 3) Try focus + Enter key
        try:
            self.page.focus(selector, timeout=int(self.timeout * 1000))
            self.page.keyboard.press("Enter")
            log.info("[AIInteractor] ✅ click via HUMAN_TYPING (Enter key) method succeeded")
            self._log_method('human_typing', start, selector, context_hint)
            return True
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ focus+Enter failed: {e}")
        
        # 4) Try dispatchEvent for click
        try:
            result = self.page.evaluate(
                """(sel) => {
                    const el = document.querySelector(sel);
                    if (!el) return false;
                    const event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    el.dispatchEvent(event);
                    return true;
                }""",
                selector,
            )
            if result:
                log.info("[AIInteractor] ✅ click via JS_DISPATCH_EVENT method succeeded")
                self._log_method('js_inject', start, selector, context_hint)
                return True
        except Exception as e:
            log.warning(f"[AIInteractor] ⚠️ JS dispatchEvent failed: {e}")
        
        # 5) All methods failed - degraded mode
        log.error(f"[AIInteractor] ❌ All click methods FAILED for selector={selector}")
        self._log_method('degraded', start, selector, context_hint, failed=True)
        return False
    
    def safe_navigate(self, url: str) -> bool:
        """
        Safely navigate to a URL with error handling.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation succeeded
        """
        start = time.perf_counter()
        log.info(f"[AIInteractor] safe_navigate url={url}")
        
        try:
            self.page.goto(url, wait_until="networkidle", timeout=int(self.timeout * 1000))
            log.info("[AIInteractor] ✅ navigate via DIRECT method succeeded")
            self._log_method('direct', start, url, "navigation")
            return True
        except Exception as e:
            log.error(f"[AIInteractor] ❌ navigation failed: {e}")
            self._log_method('degraded', start, url, "navigation", failed=True)
            return False
    
    def _log_method(
        self,
        method: str,
        start_time: float,
        selector: str,
        context_hint: str = "",
        failed: bool = False
    ):
        """
        Log interaction method and timing.
        
        Args:
            method: Interaction method used ('direct', 'js_inject', 'human_typing', 'degraded')
            start_time: Start time from time.perf_counter()
            selector: CSS selector or URL
            context_hint: Optional context description
            failed: Whether all methods failed
        """
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        entry = {
            "interaction_method": method,
            "interaction_latency_ms": round(elapsed_ms, 2),
            "selector": selector,
            "context": context_hint,
            "timestamp": time.time(),
            "failed": failed
        }
        
        self.interaction_log.append(entry)
        
        log.info(
            f"[AIInteractor] method={method} "
            f"elapsed_ms={elapsed_ms:.2f} "
            f"selector={selector} "
            f"context={context_hint} "
            f"failed={failed}"
        )
    
    def get_interaction_stats(self) -> Dict[str, int]:
        """
        Get statistics of interaction methods used.
        
        Returns:
            dict: Count of each interaction method used
            
        Example:
            >>> stats = interactor.get_interaction_stats()
            >>> print(stats)
            {'direct': 2, 'js_inject': 1, 'human_typing': 0, 'degraded': 0}
        """
        stats = {
            'direct': 0,
            'js_inject': 0,
            'human_typing': 0,
            'degraded': 0
        }
        
        for entry in self.interaction_log:
            method = entry.get('interaction_method', 'unknown')
            if method in stats:
                stats[method] += 1
        
        return stats
    
    def get_interaction_log(self) -> list:
        """
        Get full interaction log.
        
        Returns:
            list: List of interaction log entries
        """
        return self.interaction_log.copy()
    
    def clear_log(self):
        """Clear interaction log."""
        self.interaction_log.clear()
        log.info("[AIInteractor] Interaction log cleared")


# Convenience function for quick access
def create_interactor(page: Page, timeout: float = 5000) -> AIInteractor:
    """
    Create an AIInteractor instance.
    
    Args:
        page: Playwright Page object
        timeout: Timeout in milliseconds
        
    Returns:
        AIInteractor instance
    """
    return AIInteractor(page, timeout)
