"""
Git Hooks Security Service
===========================

Microservice for automated security scanning in Git workflows.

Components:
- check_private_data.py: Security scanner
- install_git_hooks.py: Hook installer
- .githooks/: Hook templates

Usage:
    # Install hooks
    python services/git_hooks/install_git_hooks.py
    
    # Manual security check
    python services/git_hooks/check_private_data.py
"""

from pathlib import Path
import subprocess
import sys

# Add service to path
SERVICE_DIR = Path(__file__).parent
sys.path.insert(0, str(SERVICE_DIR))


def run_security_scan() -> int:
    """
    Run security scan on current repository.
    
    Returns:
        0 if safe, 1 if sensitive data detected
    """
    scanner_path = SERVICE_DIR / "check_private_data.py"
    result = subprocess.run([sys.executable, str(scanner_path)])
    return result.returncode


def install_hooks() -> int:
    """
    Install Git hooks for automated security checks.
    
    Returns:
        0 if successful
    """
    installer_path = SERVICE_DIR / "install_git_hooks.py"
    result = subprocess.run([sys.executable, str(installer_path)])
    return result.returncode


__all__ = ['run_security_scan', 'install_hooks']
