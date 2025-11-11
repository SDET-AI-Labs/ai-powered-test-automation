"""
integration/test_gateway_sanity.py
-----------------------------------------------
Verifies that the AI Gateway is working correctly
for the currently selected provider in .env
-----------------------------------------------
"""

import pytest
from ai_gateway import AIGateway


@pytest.mark.sanity
def test_ai_gateway_basic_response():
    """
    Check that the AI Gateway returns a valid text response.
    This ensures the provider connection and model availability.
    """
    ai = AIGateway()
    prompt = "Say 'gateway operational' if you can read this."
    response = ai.ask(prompt)
    print("\n[AI Response]:", response)
    assert isinstance(response, str), "Response should be a string."
    assert len(response) > 5, "Response is too short — gateway may have failed."
    assert "gateway" in response.lower() or "operational" in response.lower(), \
        "Unexpected AI response content."


@pytest.mark.sanity
def test_provider_switching(monkeypatch):
    """
    Ensure that changing provider dynamically updates gateway.
    This doesn't make actual API calls, just verifies env reading.
    """
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    ai = AIGateway()
    assert ai.provider == "ollama", "Provider switch failed."
