"""
Compare AI Provider Performance
Test prompt: "playwright automation testing using AI in summary minimum words"
"""

import time
import os
from dotenv import load_dotenv
from ai_gateway import AIGateway

load_dotenv()

# Test prompt
PROMPT = "playwright automation testing using AI in summary minimum words"

# Providers to test
PROVIDERS = ["groq", "openrouter", "gemini", "openai"]

print("=" * 80)
print("🧪 AI PROVIDER COMPARISON TEST")
print("=" * 80)
print(f"Test Prompt: '{PROMPT}'")
print("=" * 80)
print()

results = []

for provider in PROVIDERS:
    # Check if provider has API key
    key_map = {
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY"
    }
    
    if not os.getenv(key_map[provider]):
        print(f"❌ {provider.upper()}: API key not found, skipping...")
        print()
        continue
    
    print(f"🔄 Testing {provider.upper()}...")
    print("-" * 80)
    
    try:
        # Set the provider via environment variable
        os.environ["AI_PROVIDER"] = provider
        gateway = AIGateway()
        
        # Measure response time
        start_time = time.time()
        response = gateway.ask(PROMPT)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Store results
        results.append({
            "provider": provider,
            "response": response,
            "time": duration,
            "word_count": len(response.split())
        })
        
        print(f"⏱️  Response Time: {duration:.2f} seconds")
        print(f"📝 Word Count: {len(response.split())} words")
        print(f"💬 Response:")
        print(response)
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()

# Summary
print("=" * 80)
print("📊 SUMMARY & RANKING")
print("=" * 80)
print()

if results:
    # Sort by response time (fastest first)
    results_by_speed = sorted(results, key=lambda x: x["time"])
    
    print("🏆 FASTEST RESPONSE:")
    fastest = results_by_speed[0]
    print(f"   Provider: {fastest['provider'].upper()}")
    print(f"   Time: {fastest['time']:.2f}s")
    print()
    
    print("📋 FULL RANKING BY SPEED:")
    for i, result in enumerate(results_by_speed, 1):
        print(f"   {i}. {result['provider'].upper()}: {result['time']:.2f}s ({result['word_count']} words)")
    print()
    
    print("💡 RESPONSE QUALITY COMPARISON:")
    print("   (Read all responses above to judge quality)")
    print()
    
    print("🎯 RECOMMENDATION:")
    print(f"   → Use {fastest['provider'].upper()} for speed")
    print(f"   → Compare response quality manually from output above")
else:
    print("No results to compare.")
