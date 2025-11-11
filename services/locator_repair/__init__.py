"""
Universal AI-Powered Locator Repair Microservice
=================================================

A framework-agnostic locator healing service that works with:
- Playwright
- Selenium
- Any other web automation framework

Architecture:
- Single AI healing core (no duplicated logic)
- Framework adapters for specific implementations
- REST API ready for microservice deployment
"""

from .repair_service import LocatorRepairService, RepairRequest, RepairResponse

__all__ = ['LocatorRepairService', 'RepairRequest', 'RepairResponse']
