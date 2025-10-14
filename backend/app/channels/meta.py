"""
Meta (Facebook Messenger & Instagram) Channel Adapter
- GET /channels/meta/webhook -> webhook verification
- POST /channels/meta/webhook -> receive messages and auto-reply
"""
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, Request, HTTPException, Header
import hmac
import hashlib
import os
import httpx

from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager
from app.core.config import settings

router = APIRouter()


# Use new configuration settings
META_VERIFY_TOKEN = settings.facebook_verify_token or "verify-token"
META_APP_SECRET = settings.facebook_app_secret

# Facebook Messenger
FACEBOOK_APP_ID = settings.facebook_app_id
FACEBOOK_APP_SECRET = settings.facebook_app_secret
FACEBOOK_PAGE_ACCESS_TOKEN = settings.facebook_page_access_token
FACEBOOK_VERIFY_TOKEN = settings.facebook_verify_token

# Instagram Business
INSTAGRAM_BUSINESS_ID = settings.instagram_business_id
INSTAGRAM_ACCESS_TOKEN = settings.instagram_access_token

# Legacy support
MESSENGER_PAGE_ID = FACEBOOK_PAGE_ACCESS_TOKEN  # Keep backward compatibility
MESSENGER_PAGE_ACCESS_TOKEN = FACEBOOK_PAGE_ACCESS_TOKEN


def verify_signature(x_hub_signature_256: Optional[str], body: bytes) -> bool:
    if not META_APP_SECRET or not x_hub_signature_256:
        return True
    try:
        expected = "sha256=" + hmac.new(META_APP_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, x_hub_signature_256)
    except Exception:
        return False


@router.get("/webhook")
async def webhook_verify(hub_mode: Optional[str] = None, hub_verify_token: Optional[str] = None, hub_challenge: Optional[str] = None):
    if hub_mode == "subscribe" and hub_verify_token == META_VERIFY_TOKEN:
        return int(hub_challenge or 0)
    raise HTTPException(status_code=403, detail="Verification failed")


async def _send_messenger(to_psid: str, text: str) -> Dict[str, Any]:
    if not MESSENGER_PAGE_ID or not MESSENGER_PAGE_ACCESS_TOKEN:
        return {"status": "skipped", "reason": "missing_messenger_credentials"}
    url = f"https://graph.facebook.com/v18.0/{MESSENGER_PAGE_ID}/messages"
    payload = {
        "recipient": {"id": to_psid},
        "message": {"text": text}
    }
    params = {"access_token": MESSENGER_PAGE_ACCESS_TOKEN}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, params=params, json=payload, timeout=15)
        return r.json()


async def _send_instagram(to_igid: str, text: str) -> Dict[str, Any]:
    if not INSTAGRAM_BUSINESS_ID or not INSTAGRAM_ACCESS_TOKEN:
        return {"status": "skipped", "reason": "missing_instagram_credentials"}
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ID}/messages"
    payload = {
        "recipient": {"id": to_igid},
        "message": {"text": text}
    }
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, params=params, json=payload, timeout=15)
        return r.json()


def _extract_events(body: Dict[str, Any]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for entry in body.get("entry", []):
        for change in entry.get("messaging", []) or entry.get("changes", []):
            # Messenger uses 'messaging'; IG webhooks often appear under 'changes'
            if "message" in change and "text" in change["message"]:
                events.append({
                    "platform": "messenger",
                    "from": change.get("sender", {}).get("id"),
                    "text": change["message"]["text"],
                })
            elif isinstance(change, dict):
                value = change.get("value", {})
                if value.get("messaging_product") == "instagram" and value.get("messages"):
                    msg = value["messages"][0]
                    if msg.get("text"):
                        events.append({
                            "platform": "instagram",
                            "from": msg.get("from"),
                            "text": msg.get("text"),
                        })
    return events


@router.post("/webhook")
async def webhook_receive(request: Request, x_hub_signature_256: Optional[str] = Header(default=None)):
    raw = await request.body()
    if not verify_signature(x_hub_signature_256, raw):
        raise HTTPException(status_code=403, detail="Invalid signature")
    body = await request.json()

    events = _extract_events(body)
    for evt in events:
        text = evt.get("text", "")
        platform = evt.get("platform")
        user_id = evt.get("from")

        nlu_res = nlu_service.resolve(text)
        dm_res = dialogue_manager.decide(
            intent=nlu_res["intent"],
            entities=nlu_res["entities"],
            context={
                "channel": platform,
                "customer_id": user_id,
                "message": text,
                "from": user_id
            }
        )
        reply = dm_res["response_text_bn"]

        if platform == "messenger":
            await _send_messenger(user_id, reply)
        elif platform == "instagram":
            await _send_instagram(user_id, reply)

    return {"status": "ok", "processed": len(events)}
