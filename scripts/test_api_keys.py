#!/usr/bin/env python3
"""Test API keys are working correctly."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_openai_key():
    """Test OpenAI API key."""
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("❌ OpenAI API key not found in environment")
            return False
        
        if not api_key.startswith("sk-"):
            print("❌ OpenAI API key format appears invalid")
            return False
        
        print("✅ OpenAI API key loaded successfully")
        return True
        
    except ImportError:
        print("⚠️  OpenAI library not installed (pip install openai)")
        return False
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False


def test_anthropic_key():
    """Test Anthropic API key."""
    try:
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            print("❌ Anthropic API key not found in environment")
            return False
        
        if not api_key.startswith("sk-ant-"):
            print("❌ Anthropic API key format appears invalid")
            return False
        
        print("✅ Anthropic API key loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")
        return False


def main():
    """Run all API key tests."""
    print("Testing API Keys Configuration")
    print("=" * 40)
    
    results = []
    
    # Test OpenAI
    results.append(test_openai_key())
    
    # Test Anthropic
    results.append(test_anthropic_key())
    
    print("=" * 40)
    
    if all(results):
        print("✅ All API keys configured correctly!")
        return 0
    else:
        print("⚠️  Some API keys need configuration")
        print("\nMake sure to:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Never commit .env to git")
        return 1


if __name__ == "__main__":
    sys.exit(main())