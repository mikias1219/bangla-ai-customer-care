"""
TTS Service for Bangla text-to-speech
Supports Google Cloud TTS, Azure, and Coqui TTS
"""
from typing import Optional, Dict, Any
import io

from app.core.config import settings


class TTSService:
    def __init__(self):
        self.provider = settings.tts_provider
        self.client = None
        
    def load_client(self):
        """Load TTS client based on provider"""
        if self.client is not None:
            return
            
        if self.provider == "google":
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
        language: str = "bn-BD",
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize Bangla text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
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
                "sample_rate": 24000
            }
        
        if self.provider == "google":
            return self._synthesize_google(text, language, voice)
        elif self.provider == "azure":
            return self._synthesize_azure(text, language, voice)
        elif self.provider == "coqui":
            return self._synthesize_coqui(text, language)
        
        return {"error": "Unknown provider"}
    
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

