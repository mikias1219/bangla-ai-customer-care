"""
TTS Service for multilingual text-to-speech
Supports OpenAI TTS, Google Cloud TTS, Azure, and Coqui TTS
"""
from typing import Optional, Dict, Any
import io
import base64
import requests

from app.core.config import settings


class TTSService:
    def __init__(self):
        self.provider = settings.tts_provider
        self.openai_voice = settings.openai_tts_voice
        self.openai_model = settings.openai_tts_model
        self.client = None
        
    def load_client(self):
        """Load TTS client based on provider"""
        if self.client is not None:
            return

        if self.provider == "openai":
            # OpenAI TTS uses HTTP API, no client initialization needed
            if not settings.openai_api_key:
                print("OpenAI API key not configured")
                self.client = "mock"
            else:
                self.client = "openai"

        elif self.provider == "google":
            try:
                from google.cloud import texttospeech
                self.client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Failed to load Google TTS: {e}")
                self.client = "mock"

        elif self.provider == "azure":
            try:
                import azure.cognitiveservices.speech as speechsdk
                speech_config = speechsdk.SpeechConfig(
                    subscription=settings.azure_speech_key,
                    region="southeastasia"
                )
                self.client = speech_config
            except Exception as e:
                print(f"Failed to load Azure TTS: {e}")
                self.client = "mock"

        elif self.provider == "coqui":
            try:
                from TTS.api import TTS
                self.client = TTS(model_name="tts_models/bn/custom/yourmodel")
            except Exception as e:
                print(f"Failed to load Coqui TTS: {e}")
                self.client = "mock"
        else:
            self.client = "mock"
    
    def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech in any language

        Args:
            text: Text to synthesize
            language: Language code (ISO 639-1 format)
            voice: Voice name (provider-specific)

        Returns:
            Dict with audio_content (bytes) and metadata
        """
        self.load_client()

        if self.client == "mock":
            # Mock response for development
            return {
                "audio_content": b"",
                "text": text,
                "provider": "mock",
                "sample_rate": 24000,
                "language": language
            }

        if self.provider == "openai":
            return self._synthesize_openai(text, language, voice)
        elif self.provider == "google":
            return self._synthesize_google(text, language, voice)
        elif self.provider == "azure":
            return self._synthesize_azure(text, language, voice)
        elif self.provider == "coqui":
            return self._synthesize_coqui(text, language)

        return {"error": "Unknown provider"}

    def _synthesize_openai(self, text: str, language: str, voice: Optional[str]) -> Dict[str, Any]:
        """Synthesize using OpenAI TTS API"""
        try:
            # OpenAI TTS voices: alloy, echo, fable, onyx, nova, shimmer
            # These voices work well with multiple languages
            voice_name = voice or self.openai_voice  # Use configured voice

            # Map language codes to OpenAI's supported formats
            # OpenAI TTS handles language detection automatically, but we can specify voice preferences
            voice_map = {
                "alloy": "alloy",    # Neutral, clear
                "echo": "echo",      # Male voice
                "fable": "fable",    # British accent, storytelling
                "onyx": "onyx",      # Deep male voice
                "nova": "nova",      # Young female voice
                "shimmer": "shimmer" # Warm female voice
            }

            selected_voice = voice_map.get(voice_name.lower(), "alloy")

            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.openai_model,  # Use configured model
                "input": text,
                "voice": selected_voice,
                "response_format": "mp3",
                "speed": 1.0
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                return {
                    "audio_content": response.content,
                    "text": text,
                    "provider": "openai",
                    "sample_rate": 24000,  # OpenAI TTS outputs 24kHz
                    "language": language,
                    "voice": selected_voice
                }
            else:
                print(f"OpenAI TTS API error: {response.status_code} - {response.text}")
                return {
                    "audio_content": b"",
                    "text": text,
                    "provider": "openai",
                    "error": f"API error: {response.status_code}",
                    "sample_rate": 24000,
                    "language": language
                }

        except Exception as e:
            print(f"OpenAI TTS synthesis error: {e}")
            return {
                "audio_content": b"",
                "text": text,
                "provider": "openai",
                "error": str(e),
                "sample_rate": 24000,
                "language": language
            }

    def _synthesize_google(self, text: str, language: str, voice: Optional[str]) -> Dict[str, Any]:
        """Synthesize using Google Cloud TTS"""
        from google.cloud import texttospeech
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice or "bn-BD-Wavenet-A"
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        return {
            "audio_content": response.audio_content,
            "text": text,
            "provider": "google",
            "sample_rate": 24000
        }
    
    def _synthesize_azure(self, text: str, language: str, voice: Optional[str]) -> Dict[str, Any]:
        """Synthesize using Azure Cognitive Services"""
        # Implementation for Azure TTS
        return {
            "audio_content": b"",
            "text": text,
            "provider": "azure",
            "sample_rate": 24000
        }
    
    def _synthesize_coqui(self, text: str, language: str) -> Dict[str, Any]:
        """Synthesize using Coqui TTS"""
        # Implementation for Coqui TTS
        audio = self.client.tts(text)
        return {
            "audio_content": audio,
            "text": text,
            "provider": "coqui",
            "sample_rate": 22050
        }


# Singleton instance
tts_service = TTSService()

