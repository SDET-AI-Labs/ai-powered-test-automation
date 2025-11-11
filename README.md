# 🤖 AI Test Foundation

AI-powered test automation framework with multiple LLM provider support and intelligent test healing.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai_test_foundation
```

### 2. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy the example environment file
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# Edit .env and add your API keys
# (Use any text editor)
```

### 4. Run Tests
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_ai_validation.py -v

# Run with output
pytest -s -v
```

## 🔑 Getting API Keys

### Groq (Recommended - Free & Fast) ⚡
1. Visit: https://console.groq.com/keys
2. Sign up for free account
3. Generate API key
4. Add to `.env`: `GROQ_API_KEY=your_key_here`

### Gemini (Backup - Free & Reliable) ✅
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### OpenAI (Optional - Paid) 💰
1. Visit: https://platform.openai.com/api-keys
2. Sign up and add payment method
3. Generate API key
4. Add to `.env`: `OPENAI_API_KEY=your_key_here`

## 🎯 Provider Selection

**Default Provider:** Groq (fastest, free)

**To switch providers**, edit `.env`:
```bash
AI_PROVIDER=groq     # Default - Fast & Free
AI_PROVIDER=gemini   # Backup #1 - Reliable
AI_PROVIDER=openai   # Paid option
```

**Provider Priority:**
1. 🥇 Groq - Fast, free, reliable (DEFAULT)
2. 🥈 Gemini - Free, stable (BACKUP)
3. 🥉 OpenAI - Paid, high quality
4. ⚠️ HuggingFace - Low priority (API deprecated)
5. 🏠 Ollama - Local only (requires server)

## 📁 Project Structure
```
ai_test_foundation/
├── core/
│   └── ai_healer.py          # AI-powered test healing
├── tests/
│   ├── integration/
│   │   ├── test_gateway_sanity.py
│   │   └── test_healer_integration.py
│   └── test_ai_validation.py
├── logs/
│   └── healing_log.json
├── ai_gateway.py              # Unified AI provider interface
├── .env.example               # Template for environment variables
├── .env                       # Your API keys (DO NOT COMMIT!)
├── .gitignore                 # Git ignore rules
└── requirements.txt           # Python dependencies
```

## ⚠️ Important Security Notes

- ✅ **DO** keep your `.env` file private
- ✅ **DO** commit `.env.example` to Git
- ❌ **DO NOT** commit `.env` to Git (contains real API keys)
- ❌ **DO NOT** share your API keys publicly
- ✅ `.gitignore` is configured to prevent accidental commits

## 🧪 Running Tests

```bash
# Run all tests with verbose output
pytest -v

# Run sanity tests only
pytest -m sanity

# Run specific test file
pytest tests/integration/test_gateway_sanity.py -v
```

## 🛠️ Troubleshooting

### SSL Certificate Errors
If you're behind a corporate proxy, Groq and Gemini are pre-configured to bypass SSL verification.

### Missing Packages
```bash
pip install -r requirements.txt
playwright install chromium
```

### Provider Not Working
1. Check API key in `.env`
2. Verify key is valid in provider console
3. Try switching to backup provider (Gemini)

## 📝 Contributing

When contributing, ensure:
1. Never commit `.env` file
2. Update `.env.example` if adding new variables
3. Test with at least 2 providers before submitting PR

## 📄 License

MIT License - Feel free to use in your projects!
