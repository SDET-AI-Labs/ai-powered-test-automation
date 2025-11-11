"""
ai_gateway.py - Unified AI Gateway
-------------------------------------------------
Supported Providers (Priority Order):
  1. ✅ Groq      (DEFAULT - free, ultra-fast, recommended)
  2. ✅ Gemini    (BACKUP #1 - free, reliable)
  3. ✅ OpenAI   (paid, stable)
  4. ⚠️  HF       (BACKUP ONLY - API deprecated/unstable)
  5. 🏠 Ollama   (local, requires server)

Toggle providers via AI_PROVIDER in .env
Default: groq
-------------------------------------------------
"""

import os
import requests
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()


class AIGateway:
    """
    Quick Toggle Guide:
    ------------------
    To switch providers, update AI_PROVIDER in .env:
    
    AI_PROVIDER=groq     # ✅ DEFAULT - Fast, free, reliable (RECOMMENDED)
    AI_PROVIDER=gemini   # ✅ BACKUP #1 - Free, stable alternative
    AI_PROVIDER=openai   # 💰 Paid, high quality
    AI_PROVIDER=hf       # ⚠️ LOW PRIORITY - API deprecated, use only as last resort
    AI_PROVIDER=ollama   # 🏠 Requires local server: ollama serve
    """

    def __init__(self):
        # Default to 'groq' if AI_PROVIDER not set (fastest, most reliable free option)
        self.provider = os.getenv("AI_PROVIDER", "groq").lower()
        print(f"[INFO] Active AI provider: {self.provider}")

        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.hf_key = os.getenv("HF_API_KEY")

        if self.provider == "openai" and self.openai_key:
            if OpenAI is None:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            self.client = OpenAI(api_key=self.openai_key)

        elif self.provider == "groq" and self.groq_key:
            if Groq is None:
                raise ImportError("Groq package not installed. Run: pip install groq")
            import httpx
            http_client = httpx.Client(verify=False)
            self.client = Groq(api_key=self.groq_key, http_client=http_client)

        elif self.provider == "gemini" and self.gemini_key:
            if genai is None:
                raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
            genai.configure(api_key=self.gemini_key)
            self.client = None

        elif self.provider == "hf" and self.hf_key:
            self.client = None

        elif self.provider == "ollama":
            self.client = None

        else:
            raise ValueError(
                f"Invalid or missing AI provider/API key: {self.provider}. "
                "Please check your .env configuration."
            )

    def ask(self, prompt: str) -> str:
        try:
            if self.provider == "openai":
                return self._ask_openai(prompt)
            elif self.provider == "groq":
                return self._ask_groq(prompt)
            elif self.provider == "gemini":
                return self._ask_gemini(prompt)
            elif self.provider == "ollama":
                return self._ask_ollama(prompt)
            elif self.provider == "hf":
                return self._ask_hf(prompt)
            else:
                raise ValueError("Unsupported AI provider.")
        except Exception as e:
            print(f"[ERROR] LLM request failed: {e}")
            return "Error or rate limit reached."

    def _ask_openai(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def _ask_groq(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def _ask_gemini(self, prompt: str) -> str:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()

    def _ask_ollama(self, prompt: str) -> str:
        try:
            payload = {"model": "llama3", "prompt": prompt}
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                stream=True,
                timeout=180,
            )
            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = line.decode("utf-8")
                    if '"response":"' in chunk:
                        full_text += chunk.split('"response":"')[1].split('"')[0]
            return full_text.strip()
        except Exception as e:
            return f"[Ollama error] {e}"

    def _ask_hf(self, prompt: str) -> str:
        return "[HF Error] HuggingFace API is currently deprecated (HTTP 410). Provider not available."


if __name__ == "__main__":
    ai = AIGateway()
    test_prompt = "Say hello from the AI Gateway unified interface."
    response = ai.ask(test_prompt)
    print("\nAI Response:", response)