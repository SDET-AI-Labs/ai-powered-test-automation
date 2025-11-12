"""
core/ai_healer.py
-------------------------------------------------
AI-Healer module: detects locator failures, asks the
LLM (via AIGateway) for an alternative selector,
retries automatically, and logs the result.

OPTIMIZATIONS (Enterprise-Grade):
  ✅ Cache Layer - Avoid redundant AI calls
  ✅ Retry + Backoff - Handle network/API failures
  ✅ Response Sanitization - Clean AI responses
  ✅ Enhanced Logging - Detailed observability
  ✅ Fallback Hierarchy - Heuristic fallback when AI fails
  ✅ Type Hints - Full type annotations
-------------------------------------------------
"""

import os
import json
import datetime
import time
import re
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page
from services.locator_repair.ai_gateway import AIGateway


class AIHealer:
    """
    AI-powered locator healing with caching, retry logic, and fallback mechanisms.
    
    Features:
        - Cache layer to avoid redundant AI calls
        - Exponential backoff retry (max 3 attempts)
        - Response sanitization for clean locator extraction
        - Enhanced logging with latency tracking
        - Heuristic fallback when AI fails
    
    Example:
        >>> healer = AIHealer()
        >>> new_locator = healer.heal_locator(page, "#old-id", "Submit button")
        >>> # Returns cached or AI-healed locator
    """
    
    def __init__(
        self, 
        log_path: str = "logs/healing_log.json",
        cache_path: str = "logs/healing_cache.json",
        enable_vision: bool = False,
        baseline_screenshot: str = None,
        current_screenshot: str = None
    ):
        """
        Initialize AI Healer with logging and caching.
        
        Args:
            log_path: Path to healing log file
            cache_path: Path to healing cache file
            enable_vision: Enable visual fallback healing (optional)
            baseline_screenshot: Path to baseline screenshot for visual comparison
            current_screenshot: Path to current screenshot for visual comparison
        """
        self.ai = AIGateway()
        self.log_path = log_path
        self.cache_path = cache_path
        self.enable_vision = enable_vision
        self.baseline_screenshot = baseline_screenshot
        self.current_screenshot = current_screenshot
        
        # Initialize VisionAnalyzer if vision enabled
        self.vision_analyzer = None
        if enable_vision:
            try:
                from core.vision_analyzer import VisionAnalyzer
                self.vision_analyzer = VisionAnalyzer(ai_gateway=self.ai)
                print("[AI-Healer] 👁️ Vision fallback enabled")
            except Exception as e:
                print(f"[AI-Healer] ⚠️ Vision fallback disabled: {e}")
        
        # Initialize cache dictionary
        self.cache: Dict[str, str] = {}
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        # Initialize log file
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                json.dump([], f)
        
        # Load cache from disk
        self._load_cache()

    # ------------------------------------------------------------
    # CACHE MANAGEMENT
    # ------------------------------------------------------------
    
    def _load_cache(self) -> None:
        """Load healing cache from disk."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"[AI-Healer] Cache load failed: {e}. Starting with empty cache.")
                self.cache = {}
        else:
            # Initialize empty cache file
            self._save_cache()
    
    def _save_cache(self) -> None:
        """Save healing cache to disk."""
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"[AI-Healer] Cache save failed: {e}")
    
    def _get_cache_key(self, framework: str, failed_locator: str, context_hint: str) -> str:
        """
        Generate cache key from framework, locator, and context.
        
        Args:
            framework: Framework name (Playwright/Selenium)
            failed_locator: The broken locator
            context_hint: Context hint for healing
            
        Returns:
            Cache key string
        """
        return f"{framework}:{failed_locator}:{context_hint}"
    
    def clear_cache(self) -> None:
        """Clear all cached healing results."""
        self.cache = {}
        self._save_cache()
        print("[AI-Healer] Cache cleared.")

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------
    
    def heal_locator(
        self, 
        page: Page, 
        failed_locator: str, 
        context_hint: str = "", 
        engine: str = "Playwright"
    ) -> str:
        """
        Called when a locator fails. Attempts to heal using cache, AI, or fallback.
        
        Healing Strategy:
            1. Check cache for previous healing
            2. If not found, call AI with retry logic
            3. If AI fails, try heuristic fallback
            4. Log healing event with source and latency
        
        Args:
            page: Playwright Page object (used to extract HTML)
            failed_locator: The locator that failed
            context_hint: Optional hint for AI (e.g., "Submit button")
            engine: Framework being used ("Playwright" or "Selenium")
            
        Returns:
            str: Healed locator string
            
        Example:
            >>> healer = AIHealer()
            >>> new_loc = healer.heal_locator(page, "#old-id", "Login button")
            >>> # Returns: "button[type='submit']"
        """
        start_time = time.perf_counter()
        
        # 1. Check cache first
        cache_key = self._get_cache_key(engine, failed_locator, context_hint)
        if cache_key in self.cache:
            cached_locator = self.cache[cache_key]
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            self._log_healing(
                old_locator=failed_locator,
                new_locator=cached_locator,
                engine=engine,
                healing_source="cache",
                latency_ms=latency_ms,
                context_hint=context_hint
            )
            
            print(f"[AI-Healer] ✅ Cache hit! Returning: {cached_locator}")
            return cached_locator
        
        # 2. Try AI healing with retry logic
        html_content = page.content()
        new_locator = self._call_ai_with_retry(
            html_content=html_content,
            failed_locator=failed_locator,
            context_hint=context_hint,
            engine=engine
        )
        
        healing_source = "ai"
        
        # 3. If AI failed, try heuristic fallback
        if new_locator == failed_locator:
            fallback_locator = self._heuristic_fallback(context_hint, engine)
            if fallback_locator:
                new_locator = fallback_locator
                healing_source = "fallback"
                print(f"[AI-Healer] 🔄 Using fallback locator: {new_locator}")
        
        # 4. If heuristic failed, try visual fallback (if enabled)
        if new_locator == failed_locator and self.vision_analyzer:
            if self.baseline_screenshot and self.current_screenshot:
                try:
                    print(f"[AI-Healer] 👁️ Attempting visual fallback...")
                    visual_diffs = self.vision_analyzer.detect_visual_anomalies(
                        self.baseline_screenshot,
                        self.current_screenshot,
                        threshold=0.85
                    )
                    if visual_diffs:
                        visual_locator = self.vision_analyzer.suggest_locator_from_visuals(
                            visual_diffs,
                            context_hint,
                            engine
                        )
                        if visual_locator:
                            new_locator = visual_locator
                            healing_source = "vision"
                            print(f"[AI-Healer] 👁️ Using vision-based locator: {new_locator}")
                except Exception as e:
                    print(f"[AI-Healer] ⚠️ Visual fallback failed: {e}")
        
        # 5. Cache successful healing
        if new_locator != failed_locator:
            self.cache[cache_key] = new_locator
            self._save_cache()
        
        # 6. Log healing event
        latency_ms = (time.perf_counter() - start_time) * 1000
        self._log_healing(
            old_locator=failed_locator,
            new_locator=new_locator,
            engine=engine,
            healing_source=healing_source,
            latency_ms=latency_ms,
            context_hint=context_hint
        )
        
        return new_locator

    # ------------------------------------------------------------
    # AI INTERACTION WITH RETRY LOGIC
    # ------------------------------------------------------------
    
    def _call_ai_with_retry(
        self,
        html_content: str,
        failed_locator: str,
        context_hint: str,
        engine: str,
        max_attempts: int = 3
    ) -> str:
        """
        Call AI with exponential backoff retry logic.
        
        Retry Strategy:
            - Attempt 1: immediate
            - Attempt 2: wait 1s
            - Attempt 3: wait 2s
            - Attempt 4: wait 4s (if max_attempts > 3)
        
        Args:
            html_content: Page HTML for context
            failed_locator: The broken locator
            context_hint: Context hint
            engine: Framework name
            max_attempts: Maximum retry attempts (default: 3)
            
        Returns:
            str: Healed locator or original if all attempts fail
        """
        prompt = self._build_prompt(html_content, failed_locator, context_hint, engine)
        
        for attempt in range(max_attempts):
            try:
                # Call AI provider
                raw_response = self.ai.ask(prompt).strip()
                
                # Sanitize response
                clean_locator = self._clean_ai_response(raw_response)
                
                print(f"[AI-Healer] ✅ AI healing successful on attempt {attempt + 1}")
                return clean_locator
                
            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                
                print(f"[AI-Healer] ⚠️ Attempt {attempt + 1}/{max_attempts} failed: {e}")
                
                if attempt < max_attempts - 1:
                    print(f"[AI-Healer] 🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[AI-Healer] ❌ AI healing failed after {max_attempts} attempts")
                    return failed_locator  # Return original on complete failure
        
        return failed_locator
    
    def _build_prompt(
        self,
        html_content: str,
        failed_locator: str,
        context_hint: str,
        engine: str
    ) -> str:
        """
        Build AI prompt for locator healing.
        
        Args:
            html_content: Page HTML
            failed_locator: Broken locator
            context_hint: Context hint
            engine: Framework name
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""
You are an automation test assistant.
The following {engine} locator failed: "{failed_locator}".
The page HTML is below.

{context_hint}

HTML START:
{html_content[:4000]}
HTML END

Suggest ONE working alternative locator (CSS or XPath) that likely matches
the same element. Respond with ONLY the locator string, without any markdown
formatting, backticks, quotes, or explanations.
"""
        return prompt

    # ------------------------------------------------------------
    # RESPONSE SANITIZATION
    # ------------------------------------------------------------
    
    def _clean_ai_response(self, response: str) -> str:
        """
        Clean and sanitize AI response to extract pure locator string.
        
        Handles:
            - Markdown code blocks (```css, ```xpath, etc.)
            - Backticks (`locator`)
            - Quotes ("locator", 'locator')
            - JSON responses ({"locator": "value"})
            - Multi-line responses (takes first line)
            - Explanatory text before/after locator
        
        Args:
            response: Raw AI response
            
        Returns:
            str: Clean locator string
            
        Example:
            >>> clean_ai_response("```css\\n#submit-btn\\n```")
            "#submit-btn"
        """
        if not response:
            return ""
        
        # Remove leading/trailing whitespace
        resp = response.strip()
        
        # Remove markdown code blocks with language specifier
        # Handle: ```css\n#submit\n``` or ```xpath\n//button\n```
        if resp.startswith("```"):
            # Find first newline after ``` (skip language specifier)
            first_newline = resp.find("\n")
            if first_newline != -1:
                # Remove ```language\n at start
                resp = resp[first_newline + 1:]
                # Remove ``` at end
                if resp.endswith("```"):
                    resp = resp[:-3]
            else:
                # No newline, just remove ```
                resp = resp.replace("```", "")
            resp = resp.strip()
        
        # Remove inline backticks
        resp = resp.strip("`")
        
        # Remove quotes
        resp = resp.strip('"\'')
        
        # Handle JSON responses like {"locator": "#element"}
        if resp.startswith("{") and resp.endswith("}"):
            try:
                # Try to parse as JSON
                data = json.loads(resp)
                if isinstance(data, dict) and "locator" in data:
                    resp = str(data["locator"])
            except:
                # If JSON parsing fails, use regex extraction
                match = re.search(r'"locator"\s*:\s*"([^"]+)"', resp)
                if match:
                    resp = match.group(1)
                else:
                    # Fallback: extract any quoted string
                    match = re.search(r'["\']([^"\']+)["\']', resp)
                    if match:
                        resp = match.group(1)
        
        # Handle "locator: value" format
        if "locator:" in resp.lower():
            # Extract value after "locator:"
            parts = resp.split(":", 1)
            if len(parts) > 1:
                resp = parts[1].strip().strip('"\'')
        
        # Take only first line if multi-line
        if "\n" in resp:
            resp = resp.split("\n")[0].strip()
        
        # Remove any remaining whitespace
        resp = resp.strip()
        
        return resp

    # ------------------------------------------------------------
    # HEURISTIC FALLBACK
    # ------------------------------------------------------------
    
    def _heuristic_fallback(self, context_hint: str, engine: str) -> Optional[str]:
        """
        Heuristic fallback when AI healing fails completely.
        
        Strategy:
            - Extract keywords from context_hint
            - Generate generic locators based on keywords
            - Prioritize semantic locators (button, input, etc.)
        
        Args:
            context_hint: Context hint (e.g., "Submit button", "Login form")
            engine: Framework name
            
        Returns:
            Optional[str]: Fallback locator or None
            
        Example:
            >>> _heuristic_fallback("Submit button", "Playwright")
            "button:has-text('Submit')"
        """
        if not context_hint:
            return None
        
        hint_lower = context_hint.lower()
        
        # Extract keywords
        keywords = {
            "submit": ["submit", "send", "save"],
            "cancel": ["cancel", "close", "dismiss"],
            "login": ["login", "sign in", "log in"],
            "button": ["button", "btn"],
            "input": ["input", "field", "textbox"],
            "link": ["link", "anchor"],
            "checkbox": ["checkbox", "check"],
            "radio": ["radio"],
        }
        
        # Try to match keywords
        for element_type, patterns in keywords.items():
            for pattern in patterns:
                if pattern in hint_lower:
                    return self._generate_fallback_locator(element_type, pattern, engine)
        
        # Generic fallback based on hint words
        words = context_hint.split()
        if words:
            first_word = words[0]
            if engine == "Playwright":
                return f"text={first_word}"
            else:
                return f"//*[contains(text(), '{first_word}')]"
        
        return None
    
    def _generate_fallback_locator(
        self, 
        element_type: str, 
        keyword: str, 
        engine: str
    ) -> str:
        """
        Generate fallback locator based on element type and keyword.
        
        Args:
            element_type: Type of element (button, input, etc.)
            keyword: Keyword from context hint
            engine: Framework name
            
        Returns:
            str: Generated fallback locator
        """
        if engine == "Playwright":
            fallback_map = {
                "submit": "button[type='submit']",
                "cancel": "button:has-text('Cancel')",
                "login": "button:has-text('Login')",
                "button": f"button:has-text('{keyword}')",
                "input": "input[type='text']",
                "link": f"a:has-text('{keyword}')",
                "checkbox": "input[type='checkbox']",
                "radio": "input[type='radio']",
            }
        else:  # Selenium
            fallback_map = {
                "submit": "//button[@type='submit']",
                "cancel": "//button[contains(text(), 'Cancel')]",
                "login": "//button[contains(text(), 'Login')]",
                "button": f"//button[contains(text(), '{keyword}')]",
                "input": "//input[@type='text']",
                "link": f"//a[contains(text(), '{keyword}')]",
                "checkbox": "//input[@type='checkbox']",
                "radio": "//input[@type='radio']",
            }
        
        return fallback_map.get(element_type, f"text={keyword}" if engine == "Playwright" else f"//*[contains(text(), '{keyword}')]")

    # ------------------------------------------------------------
    # LOGGING
    # ------------------------------------------------------------
    
    def _log_healing(
        self,
        old_locator: str,
        new_locator: str,
        engine: str,
        healing_source: str = "ai",
        latency_ms: float = 0.0,
        context_hint: str = "",
        confidence: Optional[float] = None
    ) -> None:
        """
        Append healing record to JSON log with enhanced metadata.
        
        Args:
            old_locator: Original failed locator
            new_locator: Healed locator
            engine: Framework name
            healing_source: Source of healing ("cache", "ai", or "fallback")
            latency_ms: Healing latency in milliseconds
            context_hint: Context hint used
            confidence: Optional AI confidence score
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "engine": engine,
            "old_locator": old_locator,
            "new_locator": new_locator,
            "healing_source": healing_source,
            "latency_ms": round(latency_ms, 2),
            "context_hint": context_hint,
            "success": (new_locator != old_locator),
        }
        
        # Add confidence if provided
        if confidence is not None:
            entry["confidence"] = confidence
        
        try:
            with open(self.log_path, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AI-Healer] Log write failed: {e}")

    # ------------------------------------------------------------
    # DIAGNOSTIC & UTILITY METHODS
    # ------------------------------------------------------------
    
    def show_recent_healings(self, limit: int = 5) -> None:
        """
        Print the last few healing records.
        
        Args:
            limit: Number of recent records to display
        """
        try:
            with open(self.log_path, "r") as f:
                data = json.load(f)
            
            print("\n--- Recent Healing Events ---")
            for entry in data[-limit:]:
                print(json.dumps(entry, indent=2))
        except Exception as e:
            print(f"[AI-Healer] Could not read log: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache size, hit rate, etc.
        """
        return {
            "cache_size": len(self.cache),
            "cache_keys": list(self.cache.keys())[:10]  # Show first 10 keys
        }
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """
        Get healing statistics from log file.
        
        Returns:
            Dict with healing counts by source, success rate, avg latency
        """
        try:
            with open(self.log_path, "r") as f:
                data = json.load(f)
            
            if not data:
                return {"total": 0}
            
            # Count by source
            sources = {"cache": 0, "ai": 0, "fallback": 0}
            successes = 0
            total_latency = 0.0
            
            for entry in data:
                source = entry.get("healing_source", "unknown")
                if source in sources:
                    sources[source] += 1
                
                if entry.get("success", False):
                    successes += 1
                
                total_latency += entry.get("latency_ms", 0.0)
            
            total = len(data)
            
            return {
                "total_healings": total,
                "by_source": sources,
                "success_rate": round(successes / total * 100, 2) if total > 0 else 0,
                "avg_latency_ms": round(total_latency / total, 2) if total > 0 else 0,
                "cache_hit_rate": round(sources["cache"] / total * 100, 2) if total > 0 else 0
            }
        except Exception as e:
            print(f"[AI-Healer] Could not calculate stats: {e}")
            return {"error": str(e)}

