from typing import Any, Dict, Optional, List
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu_service import nlu_service
from app.services.openai_service import openai_service
from app.services.product_inquiry_service import product_inquiry_service

router = APIRouter()


class NLUResolveRequest(BaseModel):
    text: str
    lang: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class NLUResolveResponse(BaseModel):
    intent: str
    entities: Dict[str, Any]
    confidence: float
    language: str
    model_used: Optional[str] = None


class ChatRequest(BaseModel):
    text: str
    channel: Optional[str] = "webchat"
    user_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    entities: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


@router.post("/resolve", response_model=NLUResolveResponse)
async def resolve(req: NLUResolveRequest) -> NLUResolveResponse:
    """Resolve intent and entities from Bangla text using OpenAI-powered NLU service"""
    result = await nlu_service.resolve(req.text, req.context)

    return NLUResolveResponse(
        intent=result["intent"],
        entities=result["entities"],
        confidence=result["confidence"],
        language=result.get("language", "unknown"),
        model_used=result.get("model_used")
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Complete chat endpoint with GPT-powered natural language responses
    Handles: NLU → Intent Classification → Product Lookup → GPT Response Generation
    """
    try:
        # Step 1: Understand the user's intent
        nlu_result = await nlu_service.resolve(req.text, req.context or {})
        intent = nlu_result.get("intent", "fallback")
        entities = nlu_result.get("entities", {})
        confidence = nlu_result.get("confidence", 0.0)
        
        # Step 2: Build context for GPT
        conversation_context = []
        if req.conversation_history:
            conversation_context = req.conversation_history[-5:]  # Last 5 messages
        
        # Step 3: Check if this is a product inquiry and fetch real data
        product_info = None
        if intent in ["product_inquiry", "price_inquiry", "availability_inquiry"]:
            product_name = entities.get("product_name")
            if product_name:
                products = await product_inquiry_service.search_products(product_name)
                if products:
                    product_info = products[0]  # Get the first matching product
        
        # Step 4: Build system prompt for GPT
        system_prompt = f"""You are a helpful AI customer service agent for an e-commerce platform.
You speak naturally in multiple languages including Bangla, English, Hindi, Arabic, and Urdu.
Always respond in the same language the customer used.

Current conversation context:
- Intent detected: {intent}
- User's message: {req.text}
- Channel: {req.channel}

Guidelines:
- Be friendly, helpful, and professional
- Keep responses concise (2-3 sentences max)
- If you detect an order-related question, ask for the order number if not provided
- If you detect a product inquiry, provide details about the product
- If you don't have specific information, politely say so and offer to help differently
- Use the customer's language naturally"""

        if product_info:
            system_prompt += f"""

Product information found:
- Name: {product_info.get('name')}
- Price: ${product_info.get('price', 'N/A')}
- Description: {product_info.get('description', 'No description available')}
- Stock: {"Available" if product_info.get('stock', 0) > 0 else "Out of stock"}"""
        
        # Step 5: Generate response using GPT
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in conversation_context:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        # Add current message
        messages.append({"role": "user", "content": req.text})
        
        # Get GPT response
        gpt_response = await openai_service.generate_response(
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return ChatResponse(
            response=gpt_response,
            intent=intent,
            confidence=confidence,
            entities=entities,
            metadata={
                "channel": req.channel,
                "user_id": req.user_id,
                "product_found": product_info is not None,
                "model": "gpt-4o-mini"
            }
        )
        
    except Exception as e:
        # Fallback response if something fails
        import logging
        logging.error(f"Chat endpoint error: {str(e)}")
        
        fallback_response = "আমি দুঃখিত, আমি এই মুহূর্তে আপনার প্রশ্নের উত্তর দিতে পারছি না। অনুগ্রহ করে একটু পরে আবার চেষ্টা করুন বা আরো বিস্তারিত করে বলুন।"
        
        if "english" in req.text.lower() or not any(char in req.text for char in "আইউএওকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎংঃঁ"):
            fallback_response = "I'm sorry, I'm having trouble understanding your request right now. Could you please try again or rephrase your question?"
        
        return ChatResponse(
            response=fallback_response,
            intent="fallback",
            confidence=0.0,
            entities={},
            metadata={"error": str(e)}
        )
