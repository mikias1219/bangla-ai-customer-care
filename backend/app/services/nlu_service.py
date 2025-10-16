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
        # Multi-language intent examples
        self.intent_examples = {
            "order_status": [
                # Bangla
                "আমার অর্ডার কোথায়?", "অর্ডার স্ট্যাটাস কি?", "আমার প্রোডাক্ট কবে আসবে?",
                # English
                "Where is my order?", "Order status check", "When will my product arrive?",
                # Hindi
                "मेरा ऑर्डर कहाँ है?", "ऑर्डर की स्थिति क्या है?", "मेरा प्रोडक्ट कब आएगा?",
                # Arabic
                "أين طلبي؟", "حالة الطلب", "متى سيصل منتجي؟",
                # Urdu
                "میرا آرڈر کہاں ہے؟", "آرڈر کی حیثیت کیا ہے؟", "میرا پروڈکٹ کب آئے گا؟"
            ],
            "return_request": [
                # Bangla
                "প্রোডাক্ট রিটার্ন করব", "ফেরত দিতে চাই", "রিটার্ন প্রসেস কি?",
                # English
                "I want to return product", "Return process", "How to return?",
                # Hindi
                "मैं प्रोडक्ट वापस करना चाहता हूं", "वापसी प्रक्रिया क्या है?", "कैसे वापस करें?",
                # Arabic
                "أريد إرجاع المنتج", "عملية الإرجاع", "كيف أرجع؟",
                # Urdu
                "میں پروڈکٹ واپس کرنا چاہتا ہوں", "واپسی کی عمل کیا ہے؟", "کیسے واپس کریں؟"
            ],
            "product_inquiry": [
                # Bangla
                "এই প্রোডাক্ট আছে?", "প্রোডাক্ট ডিটেলস বলুন", "কত দাম?",
                # English
                "Is this product available?", "Product details", "What is the price?",
                # Hindi
                "यह प्रोडक्ट उपलब्ध है?", "प्रोडक्ट की डिटेल्स बताएं", "कीमत क्या है?",
                # Arabic
                "هل هذا المنتج متوفر؟", "تفاصيل المنتج", "ما السعر؟",
                # Urdu
                "کیا یہ پروڈکٹ دستیاب ہے؟", "پروڈکٹ کی تفصیلات بتائیں", "قیمت کیا ہے؟"
            ],
            "payment_issue": [
                # Bangla
                "পেমেন্ট হয়নি", "টাকা কাটেনি", "পেমেন্ট ফেইলড",
                # English
                "Payment not received", "Money not deducted", "Payment failed",
                # Hindi
                "भुगतान नहीं हुआ", "पैसे नहीं कटे", "भुगतान विफल",
                # Arabic
                "لم يتم الدفع", "لم يتم خصم المال", "فشل الدفع",
                # Urdu
                "ادائیگی نہیں ہوئی", "پیسے نہیں کٹے", "ادائیگی ناکام"
            ],
            "delivery_tracking": [
                # Bangla
                "ডেলিভারি কোথায়?", "কুরিয়ার স্ট্যাটাস", "প্রোডাক্ট রোডে আছে?",
                # English
                "Where is delivery?", "Courier status", "Is product on the way?",
                # Hindi
                "डिलीवरी कहाँ है?", "कूरियर की स्थिति", "प्रोडक्ट रास्ते में है?",
                # Arabic
                "أين التسليم؟", "حالة البريد", "هل المنتج في الطريق؟",
                # Urdu
                "ڈیلیوری کہاں ہے؟", "کورئیر کی حیثیت", "کیا پروڈکٹ راستے میں ہے؟"
            ],
            "complaint": [
                # Bangla
                "সমস্যা আছে", "খারাপ সার্ভিস", "অভিযোগ করছি",
                # English
                "There is problem", "Bad service", "I want to complain",
                # Hindi
                "समस्या है", "खराब सेवा", "शिकायत करना चाहता हूं",
                # Arabic
                "يوجد مشكلة", "خدمة سيئة", "أريد الشكوى",
                # Urdu
                "مسئلہ ہے", "برا سروس", "میں شکایت کرنا چاہتا ہوں"
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
            This is a multi-language customer service system supporting Bangla, English, Hindi, Arabic, Urdu, and other languages.

            Query: "{text}"

            Available intents:
            {chr(10).join([f"- {intent}: {desc}" for intent, desc in intent_descriptions.items()])}

            Analyze the query in any language and determine the customer's intent.
            Consider common customer service scenarios across different cultures and languages.

            Respond with ONLY a JSON object in this exact format:
            {{"intent": "intent_name", "confidence": 0.95, "language": "detected_language", "reasoning": "brief explanation"}}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert multi-language customer service intent classifier supporting Bangla, English, Hindi, Arabic, Urdu, and other languages. Always return valid JSON with intent, confidence (0.0-1.0), language, and reasoning."},
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
                language = result.get('language', 'unknown')

                # Ensure intent is valid
                if intent not in self.intent_labels:
                    intent = 'fallback'
                    confidence = 0.3

                return intent, confidence, language

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Failed to parse intent classification response: {result_text}, error: {e}")
                return "fallback", 0.3, "unknown"

        except Exception as e:
            print(f"Intent classification error: {e}")
            # Fallback to keyword-based classification
            return self._classify_intent_keywords(text)

    def _classify_intent_keywords(self, text: str) -> tuple[str, float, str]:
        """
        Fallback keyword-based intent classification with language detection
        """
        text_lower = text.lower()

        # Multi-language keyword patterns
        keywords = {
            "order_status": [
                # English
                "order", "status", "where", "when", "arrive",
                # Bangla
                "অর্ডার", "কোথায়", "কবে", "আসবে", "আছে",
                # Hindi
                "ऑर्डर", "कहाँ", "कब", "आएगा", "है",
                # Arabic
                "طلب", "أين", "متى", "سيصل", "موجود",
                # Urdu
                "آرڈر", "کہاں", "کب", "آئے گا", "ہے"
            ],
            "return_request": [
                # English
                "return", "refund", "back",
                # Bangla
                "রিটার্ন", "ফেরত", "ferot",
                # Hindi
                "वापस", "रिटर्न", "वापसी",
                # Arabic
                "إرجاع", "إعادة", "رد",
                # Urdu
                "واپس", "ریٹرن", "واپسی"
            ],
            "product_inquiry": [
                # English
                "product", "available", "price", "cost", "details",
                # Bangla
                "প্রোডাক্ট", "আছে", "দাম", "ডিটেলস",
                # Hindi
                "प्रोडक्ट", "उपलब्ध", "कीमत", "विवरण",
                # Arabic
                "منتج", "متوفر", "سعر", "تفاصيل",
                # Urdu
                "پروڈکٹ", "دستیاب", "قیمت", "تفصیلات"
            ],
            "payment_issue": [
                # English
                "payment", "pay", "money", "taka", "failed",
                # Bangla
                "পেমেন্ট", "টাকা", "কাটেনি", "ফেইলড",
                # Hindi
                "भुगतान", "पैसे", "नहीं", "विफल",
                # Arabic
                "دفع", "مال", "لم", "فشل",
                # Urdu
                "ادائیگی", "پیسے", "نہیں", "ناکام"
            ],
            "delivery_tracking": [
                # English
                "delivery", "courier", "tracking", "shipped",
                # Bangla
                "ডেলিভারি", "কুরিয়ার", "রোডে", "পাঠানো",
                # Hindi
                "डिलीवरी", "कूरियर", "ट्रैकिंग", "भेजा",
                # Arabic
                "تسليم", "بريد", "تتبع", "شحن",
                # Urdu
                "ڈیلیوری", "کورئیر", "ٹریکنگ", "بھیجا"
            ],
            "complaint": [
                # English
                "complaint", "problem", "issue", "bad", "wrong",
                # Bangla
                "অভিযোগ", "সমস্যা", "খারাপ", "ভুল",
                # Hindi
                "शिकायत", "समस्या", "बुरा", "गलत",
                # Arabic
                "شكوى", "مشكلة", "سيء", "خطأ",
                # Urdu
                "شکایت", "مسئلہ", "برا", "غلط"
            ]
        }

        # Simple language detection based on script
        if any('\u0980' <= char <= '\u09FF' for char in text):
            detected_lang = "bn"  # Bangla
        elif any('\u0600' <= char <= '\u06FF' for char in text):
            detected_lang = "ar"  # Arabic
        elif any('\u0900' <= char <= '\u097F' for char in text):
            detected_lang = "hi"  # Hindi/Urdu
        else:
            detected_lang = "en"  # English or other Latin scripts

        scores = {}
        for intent, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[intent] = score

        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(0.8, 0.4 + scores[best_intent] * 0.1)
            return best_intent, confidence, detected_lang

        return "fallback", 0.3, detected_lang
    
    async def resolve(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main NLU resolution method
        """
        intent, confidence, language = await self.classify_intent(text)
        entities = await self.extract_entities(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "text": text,
            "language": language,
            "model_used": self.model,
            "context": context or {}
        }


# Singleton instance
nlu_service = NLUService()

