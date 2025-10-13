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

router = APIRouter()


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
        text = message_data.get("text", "")
        
        # NLU resolution
        nlu_result = nlu_service.resolve(text)
        
        # Dialogue decision
        dm_result = dialogue_manager.decide(
            intent=nlu_result["intent"],
            entities=nlu_result["entities"],
            context={"channel": "whatsapp", "from": message_data.get("from")}
        )
        
        return dm_result["response_text_bn"]


# Webhook endpoints
@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook"""
    # In production, get verify_token from settings
    verify_token = "your_verify_token"
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook_receive(request: Request):
    """Receive WhatsApp messages"""
    payload = await request.json()
    
    # In production, initialize adapter with real credentials
    adapter = WhatsAppAdapter(
        phone_number_id="your_phone_number_id",
        access_token="your_access_token",
        verify_token="your_verify_token"
    )
    
    message_data = adapter.parse_message(payload)
    
    if message_data:
        response_text = await adapter.process_message(message_data)
        await adapter.send_message(message_data["from"], response_text)
    
    return {"status": "ok"}

