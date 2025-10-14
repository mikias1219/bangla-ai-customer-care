#!/usr/bin/env python3
"""
Demo script showing multilingual AI capabilities
This works even without API key (shows mock responses)
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def demo_tts_capabilities():
    """Demo TTS capabilities with different languages and voices"""
    print("🎤 MULTILINGUAL TEXT-TO-SPEECH DEMO")
    print("=" * 50)

    try:
        from app.services.tts_service import tts_service

        test_cases = [
            ("Hello, this is English text-to-speech!", "en", "alloy"),
            ("Bonjour, ceci est un test en français!", "fr", "nova"),
            ("Hola, esta es una prueba en español!", "es", "shimmer"),
            ("مرحبا، هذا اختبار باللغة العربية!", "ar", "echo"),
            ("你好，这是中文语音合成测试！", "zh", "onyx"),
            ("こんにちは、これは日本語の音声合成テストです！", "ja", "fable"),
        ]

        for text, lang, voice in test_cases:
            print(f"\n🗣️  Testing {lang.upper()}: '{text[:40]}...'")
            print(f"   Voice: {voice}")

            try:
                result = tts_service.synthesize(text, language=lang, voice=voice)

                if result.get("audio_content"):
                    provider = result.get("provider", "unknown")
                    audio_size = len(result["audio_content"])
                    print(f"   ✅ Generated {audio_size} bytes of audio using {provider}")
                    print(f"   📊 Sample rate: {result.get('sample_rate', 'unknown')}Hz")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"   ❌ Failed: {error}")

            except Exception as e:
                print(f"   ❌ Exception: {e}")

    except ImportError as e:
        print(f"❌ Cannot import TTS service: {e}")
        print("   (Dependencies not installed - run: pip install -r backend/requirements.txt)")

def demo_asr_capabilities():
    """Demo ASR capabilities with auto language detection"""
    print("\n🎧 SPEECH-TO-TEXT DEMO")
    print("=" * 50)

    try:
        from app.services.asr_service import asr_service
        import numpy as np

        print("✅ Whisper ASR service loaded")
        print("📊 Supports 99+ languages with automatic detection")
        print("🎯 Features:")
        print("   • Auto language detection")
        print("   • Confidence scoring")
        print("   • Real-time processing")
        print("   • Multiple model sizes (tiny, base, small, medium, large)")

        # Test service initialization
        print(f"\n🔧 Model size: {asr_service.model_size}")
        print("✅ ASR ready for multilingual speech recognition")

    except ImportError as e:
        print(f"❌ Cannot import ASR service: {e}")

def demo_voice_integration():
    """Demo voice channel integration"""
    print("\n📞 VOICE CHANNEL INTEGRATION")
    print("=" * 50)

    print("✅ Twilio IVR Integration:")
    print("   • Webhook: /channels/voice/twilio/voice")
    print("   • Gather: /channels/voice/twilio/gather")
    print("   • Audio: /channels/voice/twilio/audio/{text}")

    print("\n✅ Asterisk/FreeSWITCH Integration:")
    print("   • Inbound: /channels/voice/voip/asterisk/inbound")
    print("   • Audio: /channels/voice/voip/asterisk/audio")
    print("   • ESL: /channels/voice/voip/freeswitch/event")

    print("\n🔊 Audio Generation Endpoints:")
    print("   GET /channels/voice/twilio/audio/{text}?lang=en&voice=alloy")
    print("   GET /channels/voice/voip/tts/{text}?voice=nova")

def demo_social_channels():
    """Demo social media channel support"""
    print("\n📱 SOCIAL MEDIA CHANNELS")
    print("=" * 50)

    channels = [
        ("Facebook Messenger", "/channels/meta/webhook", "✅ Real-time messaging"),
        ("WhatsApp Business", "/channels/whatsapp/webhook", "✅ Automated responses"),
        ("Instagram Business", "/channels/meta/webhook", "✅ DM support"),
        ("Web Chat Widget", "/channels/webchat/message", "✅ Website integration"),
    ]

    for channel, endpoint, status in channels:
        print(f"📱 {channel}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Status: {status}")
        print()

def main():
    """Main demo function"""
    print("🚀 BANGLA AI PLATFORM - MULTILINGUAL DEMO")
    print("=" * 60)
    print("Demonstrating AI capabilities for global customer service")
    print("Supports 99+ languages, 6 voices, and multiple channels")
    print()

    demo_tts_capabilities()
    demo_asr_capabilities()
    demo_voice_integration()
    demo_social_channels()

    print("\n🎉 DEMO COMPLETE!")
    print("\n📋 To test with real OpenAI API:")
    print("1. Set your API key in .env: BANG_OPENAI_API_KEY=sk-your-key")
    print("2. Start services: docker compose up -d")
    print("3. Test TTS: curl 'http://localhost:8000/channels/voice/twilio/audio/Hello'")
    print("4. Open dashboard: http://localhost:5173")
    print("\n🌍 Your AI now speaks and understands the world!")

if __name__ == "__main__":
    main()
