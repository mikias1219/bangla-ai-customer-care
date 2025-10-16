"""
WhatsApp Business API Channel Adapter
Handles incoming/outgoing messages via Meta Cloud API
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager
from app.core.config import settings

router = APIRouter()

# Use new configuration settings
WHATSAPP_BUSINESS_ID = settings.whatsapp_business_id
WHATSAPP_ACCESS_TOKEN = settings.whatsapp_access_token
WHATSAPP_VERIFY_TOKEN = settings.whatsapp_verify_token
WHATSAPP_PHONE_NUMBER_ID = settings.whatsapp_phone_number_id


class WhatsAppAdapter:
    def __init__(self, phone_number_id: str, access_token: str, verify_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.verify_token = verify_token
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def parse_message(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse incoming WhatsApp message"""
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return None
            
            message = messages[0]
            return {
                "from": message.get("from"),
                "message_id": message.get("id"),
                "timestamp": message.get("timestamp"),
                "text": message.get("text", {}).get("body", ""),
                "type": message.get("type")
            }
        except (IndexError, KeyError):
            return None
    
    async def send_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send message via WhatsApp"""
        import httpx
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            return response.json()
    
    async def process_message(self, message_data: Dict[str, Any]) -> str:
        """Process incoming message through NLU and DM"""
        from app.db.base import get_db
        from app.db.models import Conversation, Turn, ConversationStatus, TurnSpeaker
        from sqlalchemy.orm import Session
        import uuid

        text = message_data.get("text", "")
        customer_id = message_data.get("from", "unknown")

        # NLU resolution with language detection
        nlu_result = await nlu_service.resolve(text)
        detected_language = nlu_result.get("language", "bn")

        # Get database session
        db = next(get_db())

        try:
            # Find or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.customer_id == customer_id,
                Conversation.channel == "whatsapp",
                Conversation.status == ConversationStatus.active
            ).first()

            if not conversation:
                conversation_id = str(uuid.uuid4())[:8]
                conversation = Conversation(
                    conversation_id=conversation_id,
                    channel="whatsapp",
                    customer_id=customer_id,
                    customer_language=detected_language,
                    status=ConversationStatus.active
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            # Create user turn
            turn_index = len(conversation.turns) if conversation.turns else 0
            user_turn = Turn(
                conversation_id=conversation.id,
                turn_index=turn_index,
                speaker=TurnSpeaker.user,
                text=text,
                text_language=detected_language,
                intent=nlu_result["intent"],
                entities=nlu_result["entities"],
                nlu_confidence=nlu_result["confidence"]
            )
            db.add(user_turn)

            # Dialogue decision with enhanced context
            dm_result = dialogue_manager.decide(
                intent=nlu_result["intent"],
                entities=nlu_result["entities"],
                context={
                    "channel": "whatsapp",
                    "customer_id": customer_id,
                    "message": text,
                    "language": detected_language,
                    "from": message_data.get("from")
                }
            )

            # Create bot turn
            bot_turn = Turn(
                conversation_id=conversation.id,
                turn_index=turn_index + 1,
                speaker=TurnSpeaker.bot,
                text=dm_result["response_text"],
                text_language=detected_language,
                intent=nlu_result["intent"],
                entities=nlu_result["entities"],
                turn_data={"action": dm_result["action"], "metadata": dm_result["metadata"]}
            )
            db.add(bot_turn)

            # Update conversation
            conversation.last_message_at = user_turn.timestamp
            conversation.unread_count += 1
            db.commit()

            return dm_result["response_text"]

        except Exception as e:
            print(f"Error processing WhatsApp message: {e}")
            db.rollback()
            return "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
        finally:
            db.close()


# Webhook endpoints
@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook"""
    verify_token = WHATSAPP_VERIFY_TOKEN or "your_verify_token"

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return int(hub_challenge or 0)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook_receive(request: Request):
    """Receive WhatsApp messages"""
    payload = await request.json()

    # Initialize adapter with configuration settings
    if WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN:
        adapter = WhatsAppAdapter(
            phone_number_id=WHATSAPP_PHONE_NUMBER_ID,
            access_token=WHATSAPP_ACCESS_TOKEN,
            verify_token=WHATSAPP_VERIFY_TOKEN or "default_verify_token"
        )

        message_data = adapter.parse_message(payload)

        if message_data:
            response_text = await adapter.process_message(message_data)
            await adapter.send_message(message_data["from"], response_text)
    else:
        print("WhatsApp not configured - skipping message processing")

    return {"status": "ok"}

