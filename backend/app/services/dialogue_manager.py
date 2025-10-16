"""
Dialogue Manager for conversation flow and decision making
Handles state tracking, slot filling, and action decisions
"""
from typing import Dict, Any, Optional, List
from enum import Enum

from app.services.product_inquiry_service import product_inquiry_service


class ActionType(str, Enum):
    FETCH = "fetch"
    RESPOND = "respond"
    HANDOFF = "handoff"
    CLARIFY = "clarify"
    SLOT_FILL = "slot_fill"


class DialogueState:
    def __init__(self):
        self.slots: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        
    def update_slot(self, key: str, value: Any):
        self.slots[key] = value
        
    def get_slot(self, key: str) -> Optional[Any]:
        return self.slots.get(key)
    
    def has_required_slots(self, required: List[str]) -> bool:
        return all(self.slots.get(slot) is not None for slot in required)


class DialogueManager:
    def __init__(self):
        self.intent_handlers = {
            "order_status": self._handle_order_status,
            "return_request": self._handle_return_request,
            "product_inquiry": self._handle_product_inquiry,
            "price_inquiry": self._handle_price_inquiry,
            "availability_inquiry": self._handle_availability_inquiry,
            "product_info": self._handle_product_info,
            "recommendation": self._handle_recommendation,
            "purchase_intent": self._handle_purchase_intent,
            "category_browse": self._handle_category_browse,
            "payment_issue": self._handle_payment_issue,
            "delivery_tracking": self._handle_delivery_tracking,
            "complaint": self._handle_complaint,
            "fallback": self._handle_fallback
        }
        
    def decide(
        self,
        intent: str,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: Optional[DialogueState] = None
    ) -> Dict[str, Any]:
        """
        Make a decision based on intent, entities, and context

        Returns:
            Dict with action, response_text, language, and metadata
        """
        if state is None:
            state = DialogueState()

        # Update state with entities
        for key, value in entities.items():
            state.update_slot(key, value)

        # Detect language from context or entities
        detected_language = context.get('language', 'bn')

        # Get handler for intent
        handler = self.intent_handlers.get(intent, self._handle_fallback)

        result = handler(entities, context, state)
        result['language'] = detected_language

        # Convert response to appropriate language if needed
        if 'response_text' in result:
            result['response_text'] = self._localize_response(result['response_text'], detected_language)

        return result

    def _localize_response(self, text: str, language: str) -> str:
        """
        Localize response text based on detected language
        """
        # Response templates for different languages
        templates = {
            "order_status_missing": {
                "bn": "আপনার অর্ডার স্ট্যাটাস জানার জন্য অনুগ্রহ করে অর্ডার নম্বর প্রদান করুন।",
                "en": "Please provide your order number to check the status.",
                "hi": "अपना ऑर्डर नंबर प्रदान करें ताकि स्थिति जांच सके।",
                "ur": "اپنی آرڈر کی حیثیت چیک کرنے کے لیے آرڈر نمبر فراہم کریں۔",
                "ar": "يرجى تقديم رقم الطلب للتحقق من الحالة."
            },
            "order_status_checking": {
                "bn": "আপনার অর্ডার স্ট্যাটাস চেক করছি, অনুগ্রহ করে অপেক্ষা করুন...",
                "en": "Checking your order status, please wait...",
                "hi": "आपका ऑर्डर स्टेटस चेक कर रहा हूं, कृपया प्रतीक्षा करें...",
                "ur": "آپ کی آرڈر کی حیثیت چیک کر رہا ہوں، براہ مہربانی انتظار کریں...",
                "ar": "جاري فحص حالة الطلب، يرجى الانتظار..."
            },
            "return_request_missing": {
                "bn": "রিটার্নের জন্য অনুগ্রহ করে অর্ডার নম্বর প্রদান করুন।",
                "en": "Please provide your order number for return request.",
                "hi": "वापसी के लिए कृपया अपना ऑर्डर नंबर प्रदान करें।",
                "ur": "واپسی کے لیے براہ مہربانی اپنا آرڈر نمبر فراہم کریں۔",
                "ar": "يرجى تقديم رقم الطلب للإرجاع."
            },
            "return_processing": {
                "bn": "আপনার রিটার্ন রিকোয়েস্ট প্রসেস করছি...",
                "en": "Processing your return request...",
                "hi": "आपका वापसी अनुरोध संसाधित कर रहा हूं...",
                "ur": "آپ کی واپسی کی درخواست پر عمل کر رہا ہوں...",
                "ar": "جاري معالجة طلب الإرجاع..."
            },
            "payment_issue_handoff": {
                "bn": "পেমেন্ট সমস্যার জন্য আমি আপনাকে আমাদের পেমেন্ট টিমের সাথে কানেক্ট করছি। অনুগ্রহ করে অপেক্ষা করুন।",
                "en": "For payment issues, I'm connecting you with our payment team. Please wait.",
                "hi": "भुगतान समस्याओं के लिए, मैं आपको हमारी भुगतान टीम से कनेक्ट कर रहा हूं। कृपया प्रतीक्षा करें।",
                "ur": "ادائیگی کے مسائل کے لیے، میں آپ کو ہماری ادائیگی ٹیم سے جوڑ رہا ہوں۔ براہ مہربانی انتظار کریں۔",
                "ar": "للمشاكل المتعلقة بالدفع، أنا أتصل بك مع فريق الدفع لدينا. يرجى الانتظار."
            },
            "delivery_missing_order": {
                "bn": "ডেলিভারি ট্র্যাক করার জন্য অর্ডার নম্বর লাগবে। অনুগ্রহ করে বলুন।",
                "en": "Order number is required to track delivery. Please provide it.",
                "hi": "डिलीवरी ट्रैक करने के लिए ऑर्डर नंबर की आवश्यकता है। कृपया प्रदान करें।",
                "ur": "ڈیلیوری کو ٹریک کرنے کے لیے آرڈر نمبر درکار ہے۔ براہ مہربانی فراہم کریں۔",
                "ar": "رقم الطلب مطلوبة لتتبع التسليم. يرجى تقديمها."
            },
            "complaint_handoff": {
                "bn": "আপনার অভিযোগের জন্য আমি আপনাকে আমাদের কাস্টমার সার্ভিস এজেন্টের সাথে কানেক্ট করছি। অনুগ্রহ করে অপেক্ষা করুন।",
                "en": "For your complaint, I'm connecting you with our customer service agent. Please wait.",
                "hi": "आपकी शिकायत के लिए, मैं आपको हमारे ग्राहक सेवा एजेंट से कनेक्ट कर रहा हूं। कृपया प्रतीक्षा करें।",
                "ur": "آپ کی شکایت کے لیے، میں آپ کو ہمارے کسٹمر سروس ایجنٹ سے جوڑ رہا ہوں۔ براہ مہربانی انتظار کریں۔",
                "ar": "لشكواك، أنا أتصل بك مع وكيل خدمة العملاء لدينا. يرجى الانتظار."
            },
            "fallback_handoff": {
                "bn": "আমি আপনার প্রশ্নটি ঠিক বুঝতে পারছি না। আমি আপনাকে আমাদের এজেন্টের সাথে কানেক্ট করছি।",
                "en": "I cannot understand your question clearly. I'm connecting you with our agent.",
                "hi": "मैं आपका प्रश्न सही ढंग से समझ नहीं पा रहा हूं। मैं आपको हमारे एजेंट से कनेक्ट कर रहा हूं।",
                "ur": "میں آپ کا سوال صحیح طور پر سمجھ نہیں پا رہا۔ میں آپ کو ہمارے ایجنٹ سے جوڑ رہا ہوں۔",
                "ar": "لا أستطيع فهم سؤالك بوضوح. أنا أتصل بك مع وكيلنا."
            }
        }

        # Check if text matches any template key
        for key, translations in templates.items():
            if text in translations.values():
                return translations.get(language, translations.get('en', text))

        # If no template match, return original text
        return text

    def _handle_order_status(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle order status inquiry"""
        if not state.has_required_slots(["order_id"]):
            return {
                "action": ActionType.SLOT_FILL,
                "response_text": "আপনার অর্ডার স্ট্যাটাস জানার জন্য অনুগ্রহ করে অর্ডার নম্বর প্রদান করুন।",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "order_status"
                }
            }

        return {
            "action": ActionType.FETCH,
            "response_text": "আপনার অর্ডার স্ট্যাটাস চেক করছি, অনুগ্রহ করে অপেক্ষা করুন...",
            "metadata": {
                "resolver": "order_status",
                "order_id": state.get_slot("order_id")
            }
        }
    
    def _handle_return_request(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle return/refund request"""
        if not state.has_required_slots(["order_id"]):
            return {
                "action": ActionType.SLOT_FILL,
                "response_text": "রিটার্নের জন্য অনুগ্রহ করে অর্ডার নম্বর প্রদান করুন।",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "return_request"
                }
            }

        return {
            "action": ActionType.FETCH,
            "response_text": "আপনার রিটার্ন রিকোয়েস্ট প্রসেস করছি...",
            "metadata": {
                "resolver": "return_request",
                "order_id": state.get_slot("order_id")
            }
        }
    
    def _handle_product_inquiry(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle product-related queries with instant database responses"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        # Use the product inquiry service for instant responses
        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "product_inquiry",
                **result.get("metadata", {})
            }
        }

    def _handle_price_inquiry(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle price-specific inquiries"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "price_inquiry",
                **result.get("metadata", {})
            }
        }

    def _handle_availability_inquiry(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle availability/stock inquiries"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "availability_inquiry",
                **result.get("metadata", {})
            }
        }

    def _handle_product_info(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle product information requests"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "product_info",
                **result.get("metadata", {})
            }
        }

    def _handle_recommendation(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle product recommendation requests"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "recommendation",
                **result.get("metadata", {})
            }
        }

    def _handle_purchase_intent(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle purchase/order intentions"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "purchase_intent",
                "intent": "purchase",
                **result.get("metadata", {})
            }
        }

    def _handle_category_browse(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle category browsing requests"""
        customer_message = context.get("message", "")
        customer_id = context.get("customer_id")

        result = product_inquiry_service.handle_product_query(
            customer_message, entities, customer_id
        )

        return {
            "action": ActionType.RESPOND,
            "response_text": result["response_text"],
            "metadata": {
                "auto_responded": True,
                "query_type": "category_browse",
                **result.get("metadata", {})
            }
        }
    
    def _handle_payment_issue(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle payment-related issues"""
        return {
            "action": ActionType.HANDOFF,
            "response_text": "Payment issue er jonno ami apnake amader payment team er sathe connect korchi. Ektu wait korun please.",
            "metadata": {
                "reason": "payment_issue",
                "priority": "high"
            }
        }
    
    def _handle_delivery_tracking(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle delivery tracking"""
        if not state.has_required_slots(["order_id"]):
            return {
                "action": ActionType.SLOT_FILL,
                "response_text": "Delivery track korte apnar order number lagbe. Bolun please.",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "delivery_tracking"
                }
            }
        
        return {
            "action": ActionType.FETCH,
            "response_text": "Delivery status check korchi...",
            "metadata": {
                "resolver": "delivery_tracking",
                "order_id": state.get_slot("order_id")
            }
        }
    
    def _handle_complaint(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle customer complaints"""
        return {
            "action": ActionType.HANDOFF,
            "response_text": "Apnar complaint er jonno ami apnake amader customer service agent er sathe connect korchi. Ektu oppokha korun.",
            "metadata": {
                "reason": "complaint",
                "priority": "high"
            }
        }
    
    def _handle_fallback(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        state: DialogueState
    ) -> Dict[str, Any]:
        """Handle fallback when intent is unclear"""
        return {
            "action": ActionType.HANDOFF,
            "response_text": "Ami apnar prosno ta thik bujhte parchi na. Ami apnake amader agent er sathe connect korchi.",
            "metadata": {
                "reason": "low_confidence",
                "priority": "normal"
            }
        }


# Singleton instance
dialogue_manager = DialogueManager()

