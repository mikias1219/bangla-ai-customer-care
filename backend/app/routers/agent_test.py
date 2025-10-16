from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.tenant import get_current_tenant, TenantContext
from app.db.session import get_db
from app.db.models import Client
from app.services.openai_service import openai_service
from app.services.dialogue_manager import dialogue_manager

router = APIRouter()


class TestAgentRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    language: str = "bn"


class TestAgentResponse(BaseModel):
    response: str
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

        # For now, use a simple OpenAI completion
        # In the future, this could use tenant-specific models/training data

        system_prompt = f"""You are a helpful AI assistant for {client.business_name}, a {client.business_type} business in Bangladesh.
You should respond in {request.language} language and be helpful, friendly, and professional.
Business details: {client.business_address}, Contact: {client.contact_person} ({client.contact_email})
Context: {request.context if request.context else 'General business inquiry'}"""

        user_message = request.message

        # Call OpenAI service
        response = await openai_service.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
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
            response=response.get('content', 'Sorry, I could not generate a response.'),
            intent=intent,
            entities=entities,
            confidence=confidence,
            tokens_used=response.get('usage', {}).get('total_tokens'),
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
