"""
VoIP Integration for Asterisk/FreeSWITCH
Supports SIP/VoIP connections for voice calls with AI agent
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager
from app.services.tts_service import tts_service
from app.services.asr_service import asr_service
import json
import io
import numpy as np
from typing import Optional

router = APIRouter()


@router.post("/asterisk/inbound")
async def asterisk_inbound_call(request: Request) -> Response:
    """
    Handle inbound calls from Asterisk/FreeSWITCH
    Expects JSON payload with call details
    """
    try:
        data = await request.json()
        call_id = data.get("call_id", "")
        caller_id = data.get("caller_id", "")

        # Initialize conversation
        initial_response = {
            "action": "speak",
            "text": "স্বাগতম, বাংলা এআই কাস্টমার সার্ভিসে। আপনার প্রশ্ন বলুন।",
            "language": "bn",
            "next_action": "listen"
        }

        return Response(
            content=json.dumps(initial_response),
            media_type="application/json"
        )

    except Exception as e:
        print(f"Asterisk inbound call error: {e}")
        return Response(
            content=json.dumps({"error": "Internal server error"}),
            media_type="application/json",
            status_code=500
        )


@router.post("/asterisk/audio")
async def asterisk_audio_processing(request: Request) -> Response:
    """
    Process audio from Asterisk/FreeSWITCH
    Expects audio data and processes through ASR -> NLU -> DM -> TTS
    """
    try:
        # Get audio data (assuming base64 encoded or raw audio)
        data = await request.json()
        audio_b64 = data.get("audio", "")
        call_id = data.get("call_id", "")

        if not audio_b64:
            return Response(
                content=json.dumps({"error": "No audio data"}),
                media_type="application/json",
                status_code=400
            )

        # Decode audio
        import base64
        audio_bytes = base64.b64decode(audio_b64)

        # Convert to numpy array for ASR
        # This is a simplified conversion - in production, proper audio format handling needed
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)

        # Transcribe speech to Bangla text
        asr_result = asr_service.transcribe(audio_array, language="bn")
        user_text = asr_result.get("text", "").strip()

        if not user_text:
            response = {
                "action": "speak",
                "text": "দুঃখিত, আপনার কথা বুঝতে পারলাম না। অনুগ্রহ করে আবার বলুন।",
                "language": "bn",
                "next_action": "listen"
            }
            return Response(content=json.dumps(response), media_type="application/json")

        # Process through NLU and Dialogue Manager
        nlu_res = nlu_service.resolve(user_text)
        dm_res = dialogue_manager.decide(nlu_res["intent"], nlu_res["entities"], {"channel": "voice"})

        reply_text = dm_res["response_text_bn"]

        # Generate TTS response
        tts_result = tts_service.synthesize(reply_text, language="bn-BD")

        if tts_result.get("audio_content"):
            # Return audio response
            audio_b64_response = base64.b64encode(tts_result["audio_content"]).decode('utf-8')
            response = {
                "action": "play_audio",
                "audio": audio_b64_response,
                "text": reply_text,  # Fallback text
                "next_action": "listen"
            }
        else:
            # Fallback to text-only response
            response = {
                "action": "speak",
                "text": reply_text,
                "language": "bn",
                "next_action": "listen"
            }

        return Response(content=json.dumps(response), media_type="application/json")

    except Exception as e:
        print(f"Asterisk audio processing error: {e}")
        error_response = {
            "action": "speak",
            "text": "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
            "language": "bn",
            "next_action": "hangup"
        }
        return Response(
            content=json.dumps(error_response),
            media_type="application/json",
            status_code=500
        )


@router.post("/freeswitch/event")
async def freeswitch_event(request: Request) -> Response:
    """
    Handle FreeSWITCH ESL events
    """
    try:
        data = await request.json()
        event_type = data.get("event", "")
        call_uuid = data.get("call_uuid", "")

        # Handle different FreeSWITCH events
        if event_type == "CHANNEL_ANSWER":
            # Call answered, start conversation
            response = {
                "command": "speak",
                "text": "স্বাগতম, বাংলা এআই কাস্টমার সার্ভিসে।",
                "language": "bn"
            }
        elif event_type == "DTMF":
            # Handle DTMF input
            digit = data.get("dtmf_digit", "")
            response = {
                "command": "process_input",
                "input": digit,
                "type": "dtmf"
            }
        else:
            response = {"status": "ignored", "event": event_type}

        return Response(content=json.dumps(response), media_type="application/json")

    except Exception as e:
        print(f"FreeSWITCH event error: {e}")
        return Response(
            content=json.dumps({"error": "Event processing failed"}),
            media_type="application/json",
            status_code=500
        )


@router.get("/tts/{text}")
async def generate_tts_audio(text: str, voice: Optional[str] = None) -> StreamingResponse:
    """
    Generate TTS audio for Bangla text (for direct VoIP integration)
    """
    try:
        tts_result = tts_service.synthesize(text, language="bn-BD", voice=voice)
        if tts_result.get("audio_content"):
            audio_data = io.BytesIO(tts_result["audio_content"])
            return StreamingResponse(audio_data, media_type="audio/mpeg")
        else:
            return StreamingResponse(io.BytesIO(b""), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS generation error: {e}")
        return StreamingResponse(io.BytesIO(b""), media_type="audio/mpeg")
