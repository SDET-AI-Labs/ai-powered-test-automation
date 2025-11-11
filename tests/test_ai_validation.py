import os
import pytest
from dotenv import load_dotenv
load_dotenv()

# Try to import optional dependencies; if missing, skip the test module with a clear message.
try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

if sync_playwright is None or OpenAI is None:
    missing = []
    if sync_playwright is None:
        missing.append("playwright")
    if OpenAI is None:
        missing.append("openai")
    pytest.skip(f"Skipping tests because required packages are missing: {', '.join(missing)}", allow_module_level=True)

# Ensure API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    pytest.skip("Skipping tests because OPENAI_API_KEY is not set in environment or .env", allow_module_level=True)

client = OpenAI(api_key=OPENAI_API_KEY)


def test_ai_page_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://playwright.dev/")  # any small site
        content = page.text_content("body")
        browser.close()

    prompt = f"Does this text appear to be the Playwright official homepage? Answer yes or no only.\n\n{content[:3000]}"
    # Use the OpenAI client to create a chat completion
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip().lower()
    assert "yes" in answer, f"AI validation failed: {answer}"
