"""
ASR Service for multilingual speech recognition
Uses OpenAI Whisper API for high-quality speech-to-text
"""
import base64
import io
from typing import Optional, Dict, Any, Union
import openai
from app.core.config import settings


class ASRService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "whisper-1"  # OpenAI's latest Whisper model
        print(f"ASR service initialized with OpenAI Whisper API: {self.model}")
    
    async def transcribe(
        self,
        audio_data: Union[bytes, io.BytesIO],
        language: Optional[str] = None,
        file_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using OpenAI Whisper API

        Args:
            audio_data: Audio as bytes or BytesIO object
            language: Language code (ISO 639-1), None for auto-detection
            file_format: Audio format (wav, mp3, etc.)

        Returns:
            Dict with text, confidence, and metadata
        """
        try:
            # Prepare audio file for OpenAI API
            if isinstance(audio_data, bytes):
                audio_file = io.BytesIO(audio_data)
            else:
                audio_file = audio_data

            audio_file.name = f"audio.{file_format}"  # OpenAI needs a filename

            # Call OpenAI Whisper API
            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=None,  # Auto-detect language for multi-language support
                response_format="verbose_json",  # Get detailed response with confidence
                temperature=0  # More deterministic results
            )

            # Extract confidence from segments if available
            confidence = 0.8  # Default confidence
            if hasattr(response, 'segments') and response.segments:
                # Average confidence across segments
                confidences = [seg.get('confidence', 0.8) for seg in response.segments if 'confidence' in seg]
                if confidences:
                    confidence = sum(confidences) / len(confidences)

            return {
                "text": response.text.strip(),
                "confidence": confidence,
                "language": getattr(response, 'language', language or 'bn'),
                "model_used": self.model,
                "segments": getattr(response, 'segments', []),
                "duration": getattr(response, 'duration', None)
            }

        except Exception as e:
            print(f"ASR transcription error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language or "unknown",
                "error": str(e),
                "model_used": self.model
            }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate average confidence from segments"""
        segments = result.get("segments", [])
        if not segments:
            return 0.5
        
        confidences = [seg.get("no_speech_prob", 0.5) for seg in segments]
        return 1.0 - (sum(confidences) / len(confidences))
    
    def transcribe_file(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio from file path"""
        self.load_model()

        whisper_language = None if language is None else language

        if self.model == "mock":
            result = {"text": "", "language": language or "unknown"}
        else:
            result = self.model.transcribe(
                audio_path,
                language=whisper_language,
                task="transcribe"
            )

        detected_language = result.get("language", language or "unknown")

        return {
            "text": result["text"],
            "language": detected_language,
            "language_confidence": result.get("language_probability", 0.0),
            "confidence": self._calculate_confidence(result)
        }


# Singleton instance
asr_service = ASRService()

