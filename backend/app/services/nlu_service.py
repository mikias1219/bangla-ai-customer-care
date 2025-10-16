"""
NLU Service for Bangla intent classification and entity extraction
Uses OpenAI GPT models for advanced Bangla language understanding
"""
from typing import Dict, Any, List, Optional
import re
import json
import openai
from app.core.config import settings


class NLUService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model or "gpt-4o-mini"
        self.intent_labels = [
            "order_status",      # অর্ডার স্ট্যাটাস জানতে চাই
            "return_request",    # প্রোডাক্ট রিটার্ন করতে চাই
            "product_inquiry",   # প্রোডাক্ট সম্পর্কে জানতে চাই
            "payment_issue",     # পেমেন্ট সমস্যা
            "delivery_tracking", # ডেলিভারি ট্র্যাকিং
            "complaint",         # অভিযোগ করতে চাই
            "cancel_order",      # অর্ডার ক্যানসেল করতে চাই
            "modify_order",      # অর্ডার পরিবর্তন করতে চাই
            "refund_status",     # রিফান্ড স্ট্যাটাস
            "customer_support",  # কাস্টমার সাপোর্ট চাই
            "fallback"           # অন্য কিছু
        ]

        # Bangla intent examples for better classification
        self.intent_examples = {
            "order_status": [
                "আমার অর্ডার কোথায়?", "অর্ডার স্ট্যাটাস কি?", "আমার প্রোডাক্ট কবে আসবে?",
                "My order where?", "Order status check", "When will my product arrive?"
            ],
            "return_request": [
                "প্রোডাক্ট রিটার্ন করব", "ফেরত দিতে চাই", "রিটার্ন প্রসেস কি?",
                "I want to return product", "Return process", "How to return?"
            ],
            "product_inquiry": [
                "এই প্রোডাক্ট আছে?", "প্রোডাক্ট ডিটেলস বলুন", "কত দাম?",
                "Is this product available?", "Product details", "What is the price?"
            ],
            "payment_issue": [
                "পেমেন্ট হয়নি", "টাকা কাটেনি", "পেমেন্ট ফেইলড",
                "Payment not received", "Money not deducted", "Payment failed"
            ],
            "delivery_tracking": [
                "ডেলিভারি কোথায়?", "কুরিয়ার স্ট্যাটাস", "প্রোডাক্ট রোডে আছে?",
                "Where is delivery?", "Courier status", "Is product on the way?"
            ],
            "complaint": [
                "সমস্যা আছে", "খারাপ সার্ভিস", "অভিযোগ করছি",
                "There is problem", "Bad service", "I want to complain"
            ]
        }
        
    def load_model(self):
        """Initialize OpenAI client. No model loading needed."""
        print(f"NLU service initialized with OpenAI model: {self.model}")
        return True
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using OpenAI GPT for intelligent entity recognition
        """
        try:
            prompt = f"""
            Extract relevant entities from this Bangladeshi customer service query.
            Return a JSON object with entity types and values.

            Query: "{text}"

            Entity types to extract:
            - order_id: Order numbers (e.g., #123, order 123, অর্ডার ১২৩)
            - product_name: Product names mentioned
            - phone: Phone numbers (+8801xxxxxxxxx)
            - amount: Money amounts (৳500, 500 taka)
            - email: Email addresses
            - date: Dates mentioned
            - address: Delivery/shipping addresses
            - quantity: Product quantities
            - payment_method: Payment methods mentioned

            Return only valid JSON with the extracted entities. If no entities found, return empty object {{}}.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting entities from Bangladeshi customer service queries. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )

            result_text = response.choices[0].message.content.strip()
            # Clean up the response to ensure it's valid JSON
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            try:
                entities = json.loads(result_text)
                return entities if isinstance(entities, dict) else {}
            except json.JSONDecodeError:
                print(f"Failed to parse entity extraction response: {result_text}")
                return {}

        except Exception as e:
            print(f"Entity extraction error: {e}")
            # Fallback to regex-based extraction
            return self._extract_entities_regex(text)

    def _extract_entities_regex(self, text: str) -> Dict[str, Any]:
        """
        Fallback regex-based entity extraction
        """
        entities = {}

        # Order ID pattern (e.g., #123, order 123, অর্ডার ১২৩)
        order_pattern = r'(?:order|অর্ডার|#)\s*(\d+)'
        order_match = re.search(order_pattern, text, re.IGNORECASE)
        if order_match:
            entities['order_id'] = order_match.group(1)

        # Phone number pattern (Bangladesh)
        phone_pattern = r'(?:\+?88)?01[3-9]\d{8}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            entities['phone'] = phone_match.group(0)

        # Amount pattern (e.g., ৳500, 500 taka)
        amount_pattern = r'(?:৳|টাকা|taka|tk)\s*(\d+(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, text, re.IGNORECASE)
        if amount_match:
            entities['amount'] = float(amount_match.group(1))

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            entities['email'] = email_match.group(0)

        return entities
    
    async def classify_intent(self, text: str) -> tuple[str, float]:
        """
        Classify intent using OpenAI GPT for advanced Bangla understanding
        Returns (intent, confidence)
        """
        try:
            # Create a comprehensive prompt with examples
            intent_descriptions = {
                "order_status": "Customer wants to know about their order status, delivery updates, or where their order is",
                "return_request": "Customer wants to return a product, initiate return process, or ask about return policies",
                "product_inquiry": "Customer is asking about product details, availability, specifications, or pricing",
                "payment_issue": "Customer has payment problems, payment not processed, refund issues, or money-related concerns",
                "delivery_tracking": "Customer wants delivery tracking information, courier updates, or shipping status",
                "complaint": "Customer has a complaint about service, product quality, or general dissatisfaction",
                "cancel_order": "Customer wants to cancel their order or stop the delivery",
                "modify_order": "Customer wants to change order details, quantity, address, or other modifications",
                "refund_status": "Customer wants to know about refund status or refund processing",
                "customer_support": "Customer needs general help, support, or has questions not covered by other categories",
                "fallback": "General queries that don't fit other categories"
            }

            prompt = f"""
            Classify this customer service query into the most appropriate intent category.
            Analyze the customer's intent in the context of Bangladeshi e-commerce customer service.

            Query: "{text}"

            Available intents:
            {chr(10).join([f"- {intent}: {desc}" for intent, desc in intent_descriptions.items()])}

            Consider Bangla language patterns and common customer service scenarios in Bangladesh.

            Respond with ONLY a JSON object in this exact format:
            {{"intent": "intent_name", "confidence": 0.95, "reasoning": "brief explanation"}}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Bangladeshi customer service intent classifier. Always return valid JSON with intent, confidence (0.0-1.0), and reasoning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )

            result_text = response.choices[0].message.content.strip()
            # Clean up JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            try:
                result = json.loads(result_text)
                intent = result.get('intent', 'fallback')
                confidence = float(result.get('confidence', 0.5))

                # Ensure intent is valid
                if intent not in self.intent_labels:
                    intent = 'fallback'
                    confidence = 0.3

                return intent, confidence

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Failed to parse intent classification response: {result_text}, error: {e}")
                return "fallback", 0.3

        except Exception as e:
            print(f"Intent classification error: {e}")
            # Fallback to keyword-based classification
            return self._classify_intent_keywords(text)

    def _classify_intent_keywords(self, text: str) -> tuple[str, float]:
        """
        Fallback keyword-based intent classification
        """
        text_lower = text.lower()

        keywords = {
            "order_status": ["order", "অর্ডার", "status", "কোথায়", "kothay", "আসবে", "আছে"],
            "return_request": ["return", "রিটার্ন", "ফেরত", "ferot", "ফেরত"],
            "product_inquiry": ["product", "প্রোডাক্ট", "available", "আছে", "দাম", "price"],
            "payment_issue": ["payment", "পেমেন্ট", "টাকা", "taka", "কাটেনি"],
            "delivery_tracking": ["delivery", "ডেলিভারি", "courier", "কুরিয়ার", "রোডে"],
            "complaint": ["complaint", "অভিযোগ", "problem", "সমস্যা", "খারাপ"]
        }

        scores = {}
        for intent, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[intent] = score

        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(0.8, 0.4 + scores[best_intent] * 0.1)
            return best_intent, confidence

        return "fallback", 0.3
    
    async def resolve(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main NLU resolution method
        """
        intent, confidence = await self.classify_intent(text)
        entities = await self.extract_entities(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "text": text,
            "model_used": self.model,
            "context": context or {}
        }


# Singleton instance
nlu_service = NLUService()

