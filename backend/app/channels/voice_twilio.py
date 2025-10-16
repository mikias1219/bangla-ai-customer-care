"""
Twilio Voice IVR Webhook with Bangla TTS support
- POST /channels/voice/twilio/voice -> returns greeting TwiML with <Gather>
- POST /channels/voice/twilio/gather -> receives speech/digits, runs NLU, responds with TwiML
- POST /channels/voice/twilio/audio -> streams TTS audio for Bangla responses
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response, StreamingResponse
from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager
from app.services.tts_service import tts_service
from app.services.asr_service import asr_service
import base64
import io

router = APIRouter()


def twiml(content: str) -> Response:
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>{content}</Response>"
    return Response(content=xml, media_type="application/xml")


@router.post("/voice")
async def voice_entry() -> Response:
    # For now, use English greeting since Twilio Say doesn't support Bangla well
    # In production, we'd use <Play> with TTS-generated audio
    return twiml(
        """
        <Say language="en-US">Welcome to Bangla AI Customer Service. Please speak your question in Bangla after the beep.</Say>
        <Gather input="speech dtmf" action="/channels/voice/twilio/gather" method="POST" timeout="10" language="bn-BD" />
        <Say language="en-US">We didn't receive any input. Goodbye.</Say>
        """
    )


@router.post("/gather")
async def voice_gather(SpeechResult: str = Form(default=""), Digits: str = Form(default="")) -> Response:
    user_text = SpeechResult or Digits or ""
    if not user_text:
        return twiml('<Say language="en-US">No input detected. Goodbye.</Say>')

    # Process through NLU and Dialogue Manager
    nlu_res = await nlu_service.resolve(user_text)
    dm_res = dialogue_manager.decide(nlu_res["intent"], nlu_res["entities"], {"channel": "voice"})

    # Support multiple languages - check if response has language-specific versions
    reply_text = dm_res.get("response_text", dm_res.get("response_text_en", "I understand your request."))

    # Generate TTS audio for multilingual response
    try:
        # Try to detect language from user input or use English as default
        detected_lang = "en"  # Default to English, could be enhanced with language detection
        tts_result = tts_service.synthesize(reply_text, language=detected_lang)

        if tts_result.get("audio_content"):
            # For Twilio, we need to host the audio file and provide URL
            # For now, use text response until audio hosting is implemented
            return twiml(f'<Say language="{detected_lang}">{reply_text}</Say><Gather input="speech dtmf" action="/channels/voice/twilio/gather" method="POST" timeout="10" />')
        else:
            return twiml(f'<Say language="{detected_lang}">{reply_text}</Say><Gather input="speech dtmf" action="/channels/voice/twilio/gather" method="POST" timeout="10" />')
    except Exception as e:
        print(f"TTS failed: {e}")
        return twiml(f'<Say language="en">{reply_text}</Say><Gather input="speech dtmf" action="/channels/voice/twilio/gather" method="POST" timeout="10" />')


@router.post("/audio/{text}")
async def get_audio(text: str, lang: str = "en", voice: str = "alloy") -> StreamingResponse:
    """Generate and stream TTS audio for any language"""
    try:
        tts_result = tts_service.synthesize(text, language=lang, voice=voice)
        if tts_result.get("audio_content"):
            audio_data = io.BytesIO(tts_result["audio_content"])
            return StreamingResponse(audio_data, media_type="audio/mpeg")
        else:
            # Return empty audio
            return StreamingResponse(io.BytesIO(b""), media_type="audio/mpeg")
    except Exception as e:
        print(f"Audio generation failed: {e}")
        return StreamingResponse(io.BytesIO(b""), media_type="audio/mpeg")
