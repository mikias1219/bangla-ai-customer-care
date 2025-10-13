"""
Twilio Voice IVR Webhook (minimal)
- POST /channels/voice/twilio/voice -> returns greeting TwiML with <Gather>
- POST /channels/voice/twilio/gather -> receives speech/digits, runs NLU, responds with TwiML
"""
from fastapi import APIRouter, Form
from fastapi.responses import Response
from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager

router = APIRouter()


def twiml(content: str) -> Response:
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>{content}</Response>"
    return Response(content=xml, media_type="application/xml")


@router.post("/voice")
async def voice_entry() -> Response:
    return twiml(
        """
        <Say language="en-US">Welcome to Bangla A I agent. Please say your question after the tone, then press any key.</Say>
        <Gather input="speech dtmf" action="/channels/voice/twilio/gather" method="POST" timeout="5" numDigits="1" />
        <Say>We didn't receive any input. Goodbye.</Say>
        """
    )


@router.post("/gather")
async def voice_gather(SpeechResult: str = Form(default=""), Digits: str = Form(default="")) -> Response:
    user_text = SpeechResult or Digits or ""
    if not user_text:
        return twiml("<Say>No input detected. Goodbye.</Say>")

    nlu_res = nlu_service.resolve(user_text)
    dm_res = dialogue_manager.decide(nlu_res["intent"], nlu_res["entities"], {"channel": "voice"})

    # Note: Twilio Say does not support Bangla; this is a placeholder.
    reply_text = dm_res["response_text_bn"]
    return twiml(f"<Say>{reply_text}</Say>")
