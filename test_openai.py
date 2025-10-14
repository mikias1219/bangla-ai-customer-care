#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API key configuration and functionality
"""
import sys
import os
sys.path.append('backend')

from app.core.config import settings
from app.services.openai_service import openai_service

def test_openai_config():
    """Test OpenAI configuration and basic functionality"""
    print("🧪 Testing OpenAI Configuration")
    print("=" * 50)

    # Test configuration loading
    print("🔧 Configuration Test:")
    print(f"   OpenAI API Key configured: {bool(settings.openai_api_key)}")
    print(f"   Model: {settings.openai_model}")
    print(f"   Max Tokens: {settings.openai_max_tokens}")
    print()

    if not settings.openai_api_key:
        print("❌ OpenAI API key not configured!")
        print("   Make sure BANG_OPENAI_API_KEY is set in your .env file")
        return

    # Test service initialization
    print("🔌 Service Initialization Test:")
    print(f"   Service API Key set: {bool(openai_service.api_key)}")
    print(f"   Service Model: {openai_service.model}")
    print(f"   Service Max Tokens: {openai_service.max_tokens}")
    print()

    # Test basic OpenAI call
    print("🤖 OpenAI API Test:")
    try:
        import asyncio

        async def test_async():
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in a friendly way."}
            ]

            response = await openai_service.generate_response(messages, temperature=0.5, max_tokens=50)
            print("   ✅ API call successful!")
            print(f"   Response: {response}")
            print()

            # Test sentiment analysis
            print("😊 Sentiment Analysis Test:")
            sentiment = await openai_service.analyze_sentiment("This product is amazing!")
            print(f"   Result: {sentiment}")
            print()

        asyncio.run(test_async())
        print("✅ All tests passed! OpenAI is working correctly.")

    except Exception as e:
        print(f"   ❌ API call failed: {str(e)}")
        print("   Check your API key and internet connection.")

if __name__ == "__main__":
    test_openai_config()
