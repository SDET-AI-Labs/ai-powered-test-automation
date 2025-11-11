"""
integration/test_healer_integration.py
-----------------------------------------------
Placeholder sanity test for the upcoming AI-Healer module.
Ensures architecture structure and import correctness.
-----------------------------------------------
"""

import os
import importlib

def test_ai_healer_module_exists():
    """Check that ai_healer.py exists and can be imported."""
    healer_path = os.path.join("core", "ai_healer.py")
    assert os.path.exists(healer_path), \
        "ai_healer.py not found. Did you create the core module yet?"

    spec = importlib.util.find_spec("core.ai_healer")
    assert spec is not None, "ai_healer module import failed."
