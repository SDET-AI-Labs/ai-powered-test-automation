"""
Locator Repair API Client
==========================

Client SDK for consuming the Locator Repair microservice.

This allows ANY application (Python, JavaScript, Java, etc.) to use
the repair service through HTTP requests.

Usage:
    # Python client
    from services.locator_repair.client import LocatorRepairClient
    
    client = LocatorRepairClient(base_url="http://localhost:8000")
    
    result = client.repair_locator(
        framework="playwright",
        page_source=page.content(),
        failed_locator="button#wrong",
        context_hint="Submit button"
    )
    
    if result["success"]:
        print(f"Fixed: {result['repaired_locator']}")
"""

import requests
from typing import Literal, Optional, Dict, Any


class LocatorRepairClient:
    """
    Client for Locator Repair microservice API.
    
    This allows remote access to the repair service via HTTP.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of the repair service API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if service is healthy.
        
        Returns:
            Health status response
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def repair_locator(
        self,
        framework: Literal["playwright", "selenium"],
        page_source: str,
        failed_locator: str,
        context_hint: str = ""
    ) -> Dict[str, Any]:
        """
        Repair a broken locator.
        
        Args:
            framework: Framework type (playwright or selenium)
            page_source: HTML content of the page
            failed_locator: The locator that failed
            context_hint: Optional hint about the element
            
        Returns:
            Repair response with repaired locator or error
        """
        payload = {
            "framework": framework,
            "page_source": page_source,
            "failed_locator": failed_locator,
            "context_hint": context_hint
        }
        
        response = self.session.post(
            f"{self.base_url}/api/repair",
            json=payload,
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_recent_repairs(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent repair attempts.
        
        Args:
            limit: Number of repairs to return
            
        Returns:
            List of recent repairs
        """
        response = self.session.get(
            f"{self.base_url}/api/repairs/recent",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repair service statistics.
        
        Returns:
            Statistics about repairs (success rate, framework breakdown)
        """
        response = self.session.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()


# ============================================================================
# HTTP Client Adapter (for SmartLocator)
# ============================================================================

class RemoteRepairService:
    """
    Adapter to use remote API instead of local service.
    
    This allows SmartLocator to use the microservice via HTTP.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize with API URL."""
        self.client = LocatorRepairClient(api_url)
    
    def repair_locator(
        self,
        framework: Literal["playwright", "selenium"],
        page_source: str,
        failed_locator: str,
        context_hint: str = ""
    ):
        """
        Repair locator using remote API.
        
        Returns same format as local RepairResponse for compatibility.
        """
        # Call remote API
        result = self.client.repair_locator(
            framework=framework,
            page_source=page_source,
            failed_locator=failed_locator,
            context_hint=context_hint
        )
        
        # Create compatible response object
        from dataclasses import dataclass
        from typing import Optional
        
        @dataclass
        class RemoteRepairResponse:
            success: bool
            original_locator: str
            repaired_locator: Optional[str]
            framework: str
            confidence: str
            timestamp: str
            error: Optional[str] = None
        
        return RemoteRepairResponse(
            success=result["success"],
            original_locator=result["original_locator"],
            repaired_locator=result.get("repaired_locator"),
            framework=result["framework"],
            confidence=result["confidence"],
            timestamp=result["timestamp"],
            error=result.get("error")
        )
    
    def get_recent_repairs(self, limit: int = 10):
        """Get recent repairs from remote API."""
        result = self.client.get_recent_repairs(limit)
        return result.get("repairs", [])


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Locator Repair API Client - Examples")
    print("=" * 80)
    print()
    
    # Initialize client
    client = LocatorRepairClient("http://localhost:8000")
    
    # 1. Health check
    print("1. Health Check:")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Service: {health['service']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure API server is running:")
        print("   python -m services.locator_repair.api")
    print()
    
    # 2. Repair locator
    print("2. Repair Locator:")
    try:
        result = client.repair_locator(
            framework="playwright",
            page_source="<html><button id='submit'>Submit</button></html>",
            failed_locator="button#wrong",
            context_hint="Submit button"
        )
        print(f"   Success: {result['success']}")
        print(f"   Original: {result['original_locator']}")
        print(f"   Repaired: {result['repaired_locator']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # 3. Get statistics
    print("3. Statistics:")
    try:
        stats = client.get_statistics()
        print(f"   Total Repairs: {stats['total_repairs']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   By Framework: {stats['by_framework']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    print("=" * 80)
