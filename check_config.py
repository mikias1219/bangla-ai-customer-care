#!/usr/bin/env python3
"""
Simple configuration checker for Bangla AI platform
"""
import os
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required settings"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please copy env.example to .env")
        return False

    print("✅ .env file found")

    # Check required settings
    required_settings = [
        "BANG_OPENAI_API_KEY",
        "BANG_TTS_PROVIDER",
        "BANG_WHISPER_MODEL_SIZE"
    ]

    with open(env_file, 'r') as f:
        content = f.read()

    missing = []
    for setting in required_settings:
        if setting not in content:
            missing.append(setting)
        elif f"{setting}=" in content and not any(line.strip().startswith(f"{setting}=") and '=' in line and line.split('=', 1)[1].strip() for line in content.split('\n') if line.strip()):
            missing.append(f"{setting} (empty)")

    if missing:
        print(f"❌ Missing or empty settings: {', '.join(missing)}")
        return False

    print("✅ Required settings configured")
    return True

def check_openai_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("BANG_OPENAI_API_KEY")
    if not api_key or api_key.strip() == "":
        print("❌ BANG_OPENAI_API_KEY not set in environment")
        return False

    # Mask the key for security
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✅ OpenAI API key configured: {masked_key}")
    return True

def main():
    print("🔍 Checking Bangla AI Platform Configuration")
    print("=" * 50)

    env_ok = check_env_file()
    key_ok = check_openai_key()

    if env_ok and key_ok:
        print("\n🎉 Configuration looks good!")
        print("\nYour platform now supports:")
        print("• Multilingual TTS with OpenAI (alloy, echo, fable, onyx, nova, shimmer voices)")
        print("• Automatic language detection for ASR with Whisper")
        print("• Support for 99+ languages")
        print("• High-quality voice synthesis")
        print("\nNext steps:")
        print("1. Start the services: docker-compose up -d")
        print("2. Test TTS: curl 'http://localhost:8000/channels/voice/twilio/audio/Hello%20world'")
        print("3. Check dashboard: http://localhost:5173")
    else:
        print("\n❌ Configuration issues found. Please fix before proceeding.")
        print("\nRequired setup:")
        print("1. cp env.example .env")
        print("2. Edit .env with your OpenAI API key")
        print("3. Set BANG_TTS_PROVIDER=openai")

if __name__ == "__main__":
    main()
