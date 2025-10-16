from typing import Dict, Any, Optional
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.tenant import get_current_tenant, TenantContext
from app.db.session import get_db
from app.db.models import Client
from app.services.openai_service import openai_service
from app.services.dialogue_manager import dialogue_manager

router = APIRouter()


def detect_language(text: str) -> str:
    """
    Simple language detection based on character patterns
    Returns: 'en' for English, 'bn' for Bengali, 'banglish' for mixed, 'other' for others
    """
    text = text.lower().strip()

    # Bengali characters (অ-ঌ, এ-ঐ, ও-ঔ, ক-হ, া-ৈ, ড়-ঢ়, য়)
    bengali_pattern = re.compile(r'[\u0985-\u09B9\u09BE-\u09CC\u09D7\u09DC-\u09E3\u09F0-\u09F1]')
    bengali_chars = len(bengali_pattern.findall(text))

    # English letters
    english_pattern = re.compile(r'[a-zA-Z]')
    english_chars = len(english_pattern.findall(text))

    # Numbers and symbols
    total_chars = len(re.findall(r'\w', text))

    if total_chars == 0:
        return 'en'  # Default to English

    # Calculate ratios
    bengali_ratio = bengali_chars / total_chars
    english_ratio = english_chars / total_chars

    # Language detection logic
    if bengali_ratio > 0.3 and english_ratio < 0.3:
        return 'bn'  # Mostly Bengali
    elif english_ratio > 0.7 and bengali_ratio < 0.1:
        return 'en'  # Mostly English
    elif bengali_ratio > 0.1 and english_ratio > 0.1:
        return 'banglish'  # Mixed language
    else:
        # Check for common Bengali words/phrases
        bengali_words = ['আমি', 'আপনি', 'কি', 'কেমন', 'কোথায়', 'কখন', 'কত', 'কেন', 'কি', 'এবং', 'অথবা', 'না', 'হ্যাঁ', 'ধন্যবাদ']
        if any(word in text for word in bengali_words):
            return 'bn'
        return 'en'  # Default to English


def get_language_instructions(language: str) -> str:
    """Get language-specific instructions for the AI assistant"""
    if language == 'bn':
        return """আপনি একজন সহায়ক AI সহকারী। আপনার প্রতিক্রিয়া বাংলায় হতে হবে এবং সহায়ক, বিনয়ী এবং পেশাদার হতে হবে।
আপনার উত্তরে:
- বাংলায় লিখুন
- সৌজন্যপূর্ণ এবং সহায়ক হোন
- সংক্ষিপ্ত এবং স্পষ্ট হোন
- গ্রাহকের প্রশ্নের উত্তর সঠিকভাবে দিন"""
    elif language == 'banglish':
        return """You are a helpful AI assistant. Respond in Banglish (mixed Bengali-English) and be helpful, friendly, and professional.
Your responses should:
- Use Banglish (mix of Bengali and English)
- Be polite and helpful
- Be clear and concise
- Answer customer questions accurately"""
    else:  # English and other languages
        return """You are a helpful AI assistant. Respond in English and be helpful, friendly, and professional.
Your responses should:
- Be in English
- Be polite and helpful
- Be clear and concise
- Answer customer questions accurately"""


class TestAgentRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    language: str = "bn"


class TestAgentResponse(BaseModel):
    response: str
    detected_language: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = {}
    confidence: Optional[float] = None
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None


@router.post("/test", response_model=TestAgentResponse)
async def test_agent(
    request: TestAgentRequest,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Test AI agent with a message for the current tenant.
    This endpoint allows clients to test their AI agents for free.
    """
    return await test_agent_for_tenant(request, tenant_id, db)


@router.post("/admin/test/{tenant_id}", response_model=TestAgentResponse)
async def admin_test_agent(
    tenant_id: str,
    request: TestAgentRequest,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to test AI agent for any tenant.
    This allows admins to test agents for their clients.
    """
    return await test_agent_for_tenant(request, tenant_id, db)


async def test_agent_for_tenant(
    request: TestAgentRequest,
    tenant_id: str,
    db: Session
):
    """
    Test AI agent with a message for the specified tenant.
    This endpoint allows testing AI agents for any tenant (used by both clients and admins).
    """
    try:
        # Validate tenant exists
        client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Detect language from user's message (ignore the request.language field)
        detected_language = detect_language(request.message)

        # Get language-specific instructions
        language_instructions = get_language_instructions(detected_language)

        # Create dynamic system prompt based on detected language
        if detected_language == 'bn':
            system_prompt = f"""{language_instructions}

আপনি {client.business_name} এর জন্য একজন AI সহকারী, যা বাংলাদেশের একটি {client.business_type} ব্যবসা।
ব্যবসার বিস্তারিত তথ্য: {client.business_address}, যোগাযোগ: {client.contact_person} ({client.contact_email})

প্রসঙ্গ: {request.context if request.context else 'সাধারণ ব্যবসায়িক অনুসন্ধান'}"""
        elif detected_language == 'banglish':
            system_prompt = f"""{language_instructions}

You are an AI assistant for {client.business_name}, a {client.business_type} business in Bangladesh.
Business details: {client.business_address}, Contact: {client.contact_person} ({client.contact_email})

Context: {request.context if request.context else 'General business inquiry'}"""
        else:  # English
            system_prompt = f"""{language_instructions}

You are an AI assistant for {client.business_name}, a {client.business_type} business in Bangladesh.
Business details: {client.business_address}, Contact: {client.contact_person} ({client.contact_email})

Context: {request.context if request.context else 'General business inquiry'}"""

        user_message = request.message

        # Call OpenAI service
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        response = await openai_service.generate_response(
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        # Try to analyze intent and entities (simplified)
        intent = None
        entities = {}
        confidence = 0.8

        # Basic intent detection
        message_lower = request.message.lower()
        if any(word in message_lower for word in ['price', 'cost', 'rate', 'tk', 'taka']):
            intent = 'price_inquiry'
        elif any(word in message_lower for word in ['order', 'buy', 'purchase']):
            intent = 'order_request'
        elif any(word in message_lower for word in ['location', 'address', 'where']):
            intent = 'location_inquiry'
        elif any(word in message_lower for word in ['time', 'hour', 'open', 'close']):
            intent = 'business_hours'
        else:
            intent = 'general_inquiry'

        return TestAgentResponse(
            response=response if response else ('দুঃখিত, আমি উত্তর তৈরি করতে পারিনি।' if detected_language == 'bn' else 'Sorry, I could not generate a response.'),
            detected_language=detected_language,
            intent=intent,
            entities=entities,
            confidence=confidence,
            tokens_used=None,  # Would need to modify OpenAI service to return usage
            processing_time=0.5  # Placeholder
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent test failed: {str(e)}")


@router.get("/status")
async def get_agent_status(
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Get the status of the AI agent for the current tenant.
    """
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Client not authenticated")

    return {
        "status": "active",
        "tenant_id": tenant_id,
        "client_id": client_id,
        "model": "gpt-4",
        "language_support": ["bn", "en", "banglish"],
        "features": [
            "Intent recognition",
            "Entity extraction",
            "Context awareness",
            "Multi-language support",
            "Business-specific responses"
        ]
    }


@router.post("/train")
async def train_agent(
    training_data: Dict[str, Any],
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Train the AI agent with tenant-specific data.
    This is a placeholder for future implementation.
    """
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Client not authenticated")

    # Placeholder for training functionality
    # In the future, this could update tenant-specific models

    return {
        "message": "Training initiated",
        "tenant_id": tenant_id,
        "training_data": training_data,
        "status": "processing"
    }
