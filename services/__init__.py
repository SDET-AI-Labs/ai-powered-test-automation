"""
Microservices Architecture
===========================

Clean separation of concerns with independent services:

1. Locator Repair Service (services/locator_repair/)
   - Universal AI-powered locator healing
   - Framework-agnostic (Playwright, Selenium, etc.)
   - Single source of truth for locator fixes
   
2. Git Hooks Service (services/git_hooks/)
   - Automated security scanning
   - Pre-push sensitive data detection
   - Easy installation and configuration

Usage:
    # Locator Repair
    from services.locator_repair import repair_locator
    result = repair_locator(framework="playwright", ...)
    
    # Git Hooks
    from services.git_hooks import run_security_scan, install_hooks
    run_security_scan()
"""

__all__ = ['locator_repair', 'git_hooks']
