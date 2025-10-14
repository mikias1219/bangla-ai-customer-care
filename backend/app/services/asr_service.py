"""
ASR Service for multilingual speech recognition
Uses OpenAI Whisper for all languages with auto-detection
"""
import whisper
import numpy as np
from typing import Optional, Dict, Any

from app.core.config import settings


class ASRService:
    def __init__(self):
        self.model_size = settings.whisper_model_size
        self.model = None
        
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
    
    def transcribe(
        self,
        audio_data: np.ndarray,
        language: Optional[str] = None,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text in any language

        Args:
            audio_data: Audio as numpy array
            language: Language code (ISO 639-1), None for auto-detection
            sample_rate: Audio sample rate

        Returns:
            Dict with text, confidence, and metadata
        """
        self.load_model()

        # Resample if needed (Whisper expects 16kHz)
        if sample_rate != 16000:
            # In production, use librosa or scipy for resampling
            pass

        # Use None for auto-detection, or specific language code
        whisper_language = None if language is None else language

        result = self.model.transcribe(
            audio_data,
            language=whisper_language,
            task="transcribe",
            fp16=False  # Set to True if using GPU
        )

        detected_language = result.get("language", language or "unknown")

        return {
            "text": result["text"],
            "language": detected_language,
            "language_confidence": result.get("language_probability", 0.0),
            "segments": result.get("segments", []),
            "confidence": self._calculate_confidence(result)
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

