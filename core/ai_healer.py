"""
core/ai_healer.py
-------------------------------------------------
AI-Healer module: detects locator failures, asks the
LLM (via AIGateway) for an alternative selector,
retries automatically, and logs the result.
-------------------------------------------------
"""

import os
import json
import datetime
from playwright.sync_api import Page
from ai_gateway import AIGateway


class AIHealer:
    def __init__(self, log_path: str = "logs/healing_log.json"):
        self.ai = AIGateway()
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                json.dump([], f)

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------
    def heal_locator(self, page: Page, failed_locator: str, context_hint: str = "", engine: str = "Playwright") -> str:
        """
        Called when a locator fails.
        Sends page HTML + broken locator + optional context hint to AI.
        Returns a new locator suggestion (CSS/XPath).
        
        Args:
            page: Playwright Page object (used to extract HTML)
            failed_locator: The locator that failed
            context_hint: Optional hint for AI (e.g., "Find the submit button")
            engine: The framework being used ("Playwright" or "Selenium")
        """
        html_content = page.content()
        prompt = f"""
        You are an automation test assistant.
        The following {engine} locator failed: "{failed_locator}".
        The page HTML is below.

        {context_hint}

        HTML START:
        {html_content[:4000]}   # limit for performance
        HTML END

        Suggest ONE working alternative locator (CSS or XPath) that likely matches
        the same element. Respond with ONLY the locator string, without any markdown
        formatting, backticks, quotes, or explanations.
        """

        new_locator = self.ai.ask(prompt).strip()

        # Clean the AI response - remove markdown, backticks, quotes
        new_locator = new_locator.strip('`"\'')
        # Remove common markdown patterns
        if new_locator.startswith('```') and new_locator.endswith('```'):
            new_locator = new_locator[3:-3].strip()
        # If response contains newlines, take only the first line
        if '\n' in new_locator:
            new_locator = new_locator.split('\n')[0].strip()

        # Log the healing attempt (record engine properly)
        self._log_healing(failed_locator, new_locator, engine)
        return new_locator

    # ------------------------------------------------------------
    # INTERNAL UTILITIES
    # ------------------------------------------------------------
    def _log_healing(self, old_locator: str, new_locator: str, engine: str):
        """Append healing record to JSON log."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "engine": engine,
            "old_locator": old_locator,
            "new_locator": new_locator,
        }
        try:
            with open(self.log_path, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AI-Healer] Log write failed: {e}")

    # ------------------------------------------------------------
    # Diagnostic
    # ------------------------------------------------------------
    def show_recent_healings(self, limit: int = 5):
        """Print the last few healing records."""
        with open(self.log_path, "r") as f:
            data = json.load(f)
        print("\n--- Recent Healing Events ---")
        for entry in data[-limit:]:
            print(json.dumps(entry, indent=2))
