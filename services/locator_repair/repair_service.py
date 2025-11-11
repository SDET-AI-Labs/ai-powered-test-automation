"""
Universal Locator Repair Service
=================================

A single AI-healing core that supports BOTH Playwright and Selenium.
No duplicated logic - one service, multiple framework adapters.

Usage:
    # Playwright
    from playwright.sync_api import Page
    result = service.repair_locator(
        framework="playwright",
        page_source=page.content(),
        failed_locator="button#wrong_id",
        context_hint="Submit button"
    )
    
    # Selenium
    from selenium.webdriver import Chrome
    result = service.repair_locator(
        framework="selenium",
        page_source=driver.page_source,
        failed_locator="//button[@id='wrong_id']",
        context_hint="Submit button"
    )
"""

from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime
import json
from pathlib import Path
import sys

# Import AI Gateway from core
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ai_gateway import AIGateway


@dataclass
class RepairRequest:
    """Request to repair a broken locator."""
    framework: Literal["playwright", "selenium"]
    page_source: str
    failed_locator: str
    context_hint: str = ""
    
    
@dataclass
class RepairResponse:
    """Response containing repaired locator."""
    success: bool
    original_locator: str
    repaired_locator: Optional[str]
    framework: str
    confidence: str  # high, medium, low
    timestamp: str
    error: Optional[str] = None


class LocatorRepairService:
    """
    Universal AI-powered locator repair service.
    
    This is the SINGLE SOURCE OF TRUTH for locator healing.
    Works with any web automation framework through adapters.
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        """Initialize the repair service."""
        self.ai_gateway = AIGateway()
        self.log_path = log_path or Path(__file__).parents[2] / "logs" / "healing_log.json"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def repair_locator(
        self,
        framework: Literal["playwright", "selenium"],
        page_source: str,
        failed_locator: str,
        context_hint: str = ""
    ) -> RepairResponse:
        """
        Universal locator repair method.
        
        Args:
            framework: Which framework is using this service
            page_source: HTML content of the page
            failed_locator: The locator that failed
            context_hint: Optional hint about what element we're looking for
            
        Returns:
            RepairResponse with repaired locator or error
        """
        try:
            # Build framework-agnostic prompt
            prompt = self._build_repair_prompt(
                framework=framework,
                page_source=page_source,
                failed_locator=failed_locator,
                context_hint=context_hint
            )
            
            # Call AI (single source of truth)
            ai_response = self.ai_gateway.ask(prompt)
            
            # Clean and validate response
            repaired_locator = self._clean_locator(ai_response)
            
            # Build response
            response = RepairResponse(
                success=True,
                original_locator=failed_locator,
                repaired_locator=repaired_locator,
                framework=framework,
                confidence="high",  # Can be enhanced with confidence scoring
                timestamp=datetime.now().isoformat()
            )
            
            # Log the repair
            self._log_repair(response)
            
            return response
            
        except Exception as e:
            return RepairResponse(
                success=False,
                original_locator=failed_locator,
                repaired_locator=None,
                framework=framework,
                confidence="low",
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def _build_repair_prompt(
        self,
        framework: str,
        page_source: str,
        failed_locator: str,
        context_hint: str
    ) -> str:
        """Build AI prompt for locator repair."""
        # Framework-specific syntax hints
        syntax_hints = {
            "playwright": "CSS selector or text=, role=, etc.",
            "selenium": "XPath or CSS selector"
        }
        
        prompt = f"""You are a web automation expert. A {framework} locator has failed.

FAILED LOCATOR: {failed_locator}
CONTEXT: {context_hint or "Not provided"}
FRAMEWORK: {framework} (use {syntax_hints.get(framework, 'standard')} syntax)

PAGE HTML (truncated):
{page_source[:2000]}

Analyze the HTML and suggest ONE corrected locator that will find the element.
Return ONLY the locator string, no explanations or markdown.

Rules:
- Return locator in {framework} syntax
- Must be a working selector
- No code blocks, no explanations
- Just the locator string
"""
        return prompt
    
    def _clean_locator(self, ai_response: str) -> str:
        """Clean AI response to extract pure locator."""
        locator = ai_response.strip()
        
        # Remove markdown code blocks
        if locator.startswith("```"):
            locator = locator.split("\n", 1)[1] if "\n" in locator else locator
        if locator.endswith("```"):
            locator = locator.rsplit("\n", 1)[0] if "\n" in locator else locator
            
        # Remove quotes
        locator = locator.strip('"`\'')
        
        # Take first line only
        locator = locator.split("\n")[0].strip()
        
        return locator
    
    def _log_repair(self, response: RepairResponse):
        """Log repair attempt to JSON file."""
        log_entry = {
            "timestamp": response.timestamp,
            "framework": response.framework,
            "success": response.success,
            "original_locator": response.original_locator,
            "repaired_locator": response.repaired_locator,
            "confidence": response.confidence,
            "error": response.error
        }
        
        try:
            # Append to log file
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Warning: Could not log repair: {e}")
    
    def get_recent_repairs(self, limit: int = 10) -> list[dict]:
        """Get recent repair attempts."""
        if not self.log_path.exists():
            return []
        
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Parse last N lines
            repairs = []
            for line in lines[-limit:]:
                try:
                    repairs.append(json.loads(line.strip()))
                except:
                    continue
            
            return repairs
        except Exception:
            return []


# Convenience function for quick usage
def repair_locator(
    framework: Literal["playwright", "selenium"],
    page_source: str,
    failed_locator: str,
    context_hint: str = ""
) -> RepairResponse:
    """
    Quick function to repair a locator.
    
    Example:
        result = repair_locator(
            framework="playwright",
            page_source=page.content(),
            failed_locator="button#wrong",
            context_hint="Submit button"
        )
        
        if result.success:
            element = page.locator(result.repaired_locator)
    """
    service = LocatorRepairService()
    return service.repair_locator(
        framework=framework,
        page_source=page_source,
        failed_locator=failed_locator,
        context_hint=context_hint
    )
