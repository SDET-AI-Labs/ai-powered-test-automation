"""
ai_gateway.py - Unified AI Gateway
-------------------------------------------------
Supported Providers (Priority Order):
  1. ✅ Groq        (DEFAULT - free, ultra-fast, recommended)
  2. ✅ OpenRouter  (free relay, access to DeepSeek & 200+ models)
  3. ✅ Gemini      (free, reliable)
  4. ✅ OpenAI      (paid, stable)
  5. ⚠️  HF         (BACKUP ONLY - API deprecated/unstable)
  6. 🏠 Ollama      (local, requires server)

Toggle providers via AI_PROVIDER in .env
Default: groq
-------------------------------------------------
"""

import os
import requests
import urllib3
from dotenv import load_dotenv

# Silence InsecureRequestWarning for corporate networks when verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    
    AI_PROVIDER=groq        # ✅ DEFAULT - Fast, free, reliable (RECOMMENDED)
    AI_PROVIDER=openrouter  # ✅ NEW - Free relay, DeepSeek + 200+ models
    AI_PROVIDER=gemini      # ✅ Free, stable alternative
    AI_PROVIDER=openai      # 💰 Paid, high quality
    AI_PROVIDER=hf          # ⚠️ LOW PRIORITY - API deprecated, use only as last resort
    AI_PROVIDER=ollama      # 🏠 Requires local server: ollama serve
    """

    def __init__(self):
        # Default to 'groq' if AI_PROVIDER not set (fastest, most reliable free option)
        self.provider = os.getenv("AI_PROVIDER", "groq").lower()
        print(f"[INFO] Active AI provider: {self.provider}")

        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
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

        elif self.provider == "openrouter" and self.openrouter_key:
            self.client = None

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
            elif self.provider == "openrouter":
                return self._ask_openrouter(prompt)
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
    
    def ask_vision(self, image_paths: list, question: str) -> str:
        """
        Send images + text to Vision LLM (multimodal).
        
        Supports:
            - Gemini Vision (gemini-2.0-flash-exp, gemini-1.5-flash)
            - GPT-4 Vision (gpt-4o, gpt-4o-mini)
            - OpenRouter Vision models
        
        Args:
            image_paths (list): List of image file paths
            question (str): Text prompt/question about the images
            
        Returns:
            str: LLM's analysis/description of the images
            
        Example:
            >>> response = ai.ask_vision(["screenshot1.png"], "What changed in this UI?")
        """
        try:
            # Auto-select provider: Gemini preferred, then OpenAI
            if self.provider == "gemini" or (self.provider == "openrouter" and self.gemini_key):
                return self._ask_gemini_vision(image_paths, question)
            elif self.provider == "openai":
                return self._ask_openai_vision(image_paths, question)
            elif self.provider == "openrouter":
                return self._ask_openrouter_vision(image_paths, question)
            else:
                # Fallback: Try Gemini if key exists
                if self.gemini_key:
                    print(f"[Vision] Provider '{self.provider}' doesn't support vision, falling back to Gemini")
                    return self._ask_gemini_vision(image_paths, question)
                else:
                    return "[Vision Error] No vision-capable provider available. Set GEMINI_API_KEY or OPENAI_API_KEY"
        except Exception as e:
            print(f"[ERROR] Vision LLM request failed: {e}")
            return f"Vision analysis error: {str(e)}"

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

    def _ask_openrouter(self, prompt: str) -> str:
        """Call DeepSeek (or any) model via OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "AI-TestOps-Gateway",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
        if resp.status_code != 200:
            return f"[OpenRouter Error] {resp.status_code}: {resp.text[:200]}"
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

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
    
    def _ask_gemini_vision(self, image_paths: list, question: str) -> str:
        """Call Gemini Vision API with images."""
        import base64
        from PIL import Image as PILImage
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            # Prepare images
            image_parts = []
            for img_path in image_paths:
                # Load and encode image
                img = PILImage.open(img_path)
                image_parts.append(img)
            
            # Create prompt parts
            prompt_parts = [question] + image_parts
            
            response = model.generate_content(prompt_parts)
            return response.text.strip()
            
        except Exception as e:
            print(f"[Gemini Vision Error] {e}")
            # Fallback to text-only if vision fails
            return f"[Vision Error] {str(e)}"
    
    def _ask_openai_vision(self, image_paths: list, question: str) -> str:
        """Call OpenAI GPT-4 Vision API with images."""
        import base64
        
        try:
            # Encode images to base64
            image_contents = []
            for img_path in image_paths:
                with open(img_path, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode('utf-8')
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    })
            
            # Build messages
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    *image_contents
                ]
            }]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or gpt-4o for higher quality
                messages=messages,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[OpenAI Vision Error] {e}")
            return f"[Vision Error] {str(e)}"
    
    def _ask_openrouter_vision(self, image_paths: list, question: str) -> str:
        """Call vision models via OpenRouter."""
        import base64
        
        try:
            # Encode first image
            with open(image_paths[0], "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "AI-TestOps-Gateway",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "google/gemini-2.0-flash-exp:free",  # Vision-capable model
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }],
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
            if resp.status_code != 200:
                return f"[OpenRouter Vision Error] {resp.status_code}: {resp.text[:200]}"
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            print(f"[OpenRouter Vision Error] {e}")
            return f"[Vision Error] {str(e)}"

    def _ask_hf(self, prompt: str) -> str:
        return "[HF Error] HuggingFace API is currently deprecated (HTTP 410). Provider not available."


if __name__ == "__main__":
    ai = AIGateway()
    test_prompt = "Say hello from the AI Gateway unified interface."
    response = ai.ask(test_prompt)
    print("\nAI Response:", response)