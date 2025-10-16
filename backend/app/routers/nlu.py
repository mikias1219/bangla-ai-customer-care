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
        nlu_result = await nlu_service.resolve(req.text, {})
        intent = nlu_result.get("intent", "fallback")
        entities = nlu_result.get("entities", {})
        confidence = nlu_result.get("confidence", 0.0)
        
        # Step 2: Build context for GPT
        conversation_context = []
        if req.conversation_history:
            conversation_context = req.conversation_history[-5:]  # Last 5 messages
        
        # Step 3: Check if this is a product inquiry and fetch real data
        products_data = []
        # Always search for products if the query mentions product-related keywords
        product_keywords = ['product', 'price', 'দাম', 'cost', 'buy', 'কিনতে', 'available', 'stock', 
                           'iphone', 'samsung', 'phone', 'laptop', 'watch', 'airpods', 'ফোন']
        
        if any(keyword in req.text.lower() for keyword in product_keywords):
            # Search for products in the user's query
            products_data = await product_inquiry_service.search_products(req.text)
            
            # If no products found but it's a product intent, get featured products
            if not products_data and intent in ["product_inquiry", "price_inquiry", "availability_inquiry", "recommendation"]:
                # Get featured products as suggestions
                featured = product_inquiry_service.get_featured_products(limit=5)
                products_data = [{
                    "id": p.id, "name": p.name, "description": p.description,
                    "price": p.price, "currency": p.currency, "category": p.category,
                    "brand": p.brand, "stock": p.stock_quantity, "is_featured": p.is_featured
                } for p in featured]
        
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
- Use emojis to make responses more engaging (💰 for price, 📦 for stock, ✅ for available, ❌ for out of stock)
- When showing products, format nicely with product name, price, and stock status
- If customer asks "which products do you have", list the available products from the database
- Keep responses natural and conversational, not too formal
- If you detect an order-related question, ask for the order number if not provided
- If you don't have specific information, politely say so and offer to help differently
- Use the customer's language naturally"""

        if products_data:
            system_prompt += f"""

IMPORTANT: Here are the products from our database that match the customer's query:

"""
            for idx, product in enumerate(products_data, 1):
                stock_status = "✅ In Stock" if product.get('stock', 0) > 0 else "❌ Out of Stock"
                system_prompt += f"""
Product {idx}:
- Name: {product.get('name')}
- Price: {product.get('currency', 'BDT')} {product.get('price', 0):,.2f}
- Description: {product.get('description', 'No description')}
- Category: {product.get('category', 'N/A')}
- Brand: {product.get('brand', 'N/A')}
- Stock Status: {stock_status} ({product.get('stock', 0)} units)
- SKU: {product.get('sku', 'N/A')}
"""
            
            system_prompt += f"""

Please answer the customer's question using ONLY the product information above from our database.
If they ask about products we have, list these products.
If they ask about a specific product (like iPhone or Samsung), provide its exact details from above.
Do NOT make up prices or products - use only what's provided above."""
        
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
            max_tokens=300  # Increased for product listings
        )
        
        return ChatResponse(
            response=gpt_response,
            intent=intent,
            confidence=confidence,
            entities=entities,
            metadata={
                "channel": req.channel,
                "user_id": req.user_id,
                "products_found": len(products_data),
                "products": [p.get('name') for p in products_data] if products_data else [],
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
