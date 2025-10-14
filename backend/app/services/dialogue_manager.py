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
            Dict with action, response_text_bn, and metadata
        """
        if state is None:
            state = DialogueState()
        
        # Update state with entities
        for key, value in entities.items():
            state.update_slot(key, value)
        
        # Get handler for intent
        handler = self.intent_handlers.get(intent, self._handle_fallback)
        
        return handler(entities, context, state)
    
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
                "response_text_bn": "Apnar order number ta bolun please.",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "order_status"
                }
            }
        
        return {
            "action": ActionType.FETCH,
            "response_text_bn": "Apnar order status check korchi, ektu oppokha korun...",
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
                "response_text_bn": "Return er jonno apnar order number dorkar. Order number bolun please.",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "return_request"
                }
            }
        
        return {
            "action": ActionType.FETCH,
            "response_text_bn": "Apnar return request process korchi...",
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": result["response_text"],
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
            "response_text_bn": "Payment issue er jonno ami apnake amader payment team er sathe connect korchi. Ektu wait korun please.",
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
                "response_text_bn": "Delivery track korte apnar order number lagbe. Bolun please.",
                "metadata": {
                    "missing_slots": ["order_id"],
                    "intent": "delivery_tracking"
                }
            }
        
        return {
            "action": ActionType.FETCH,
            "response_text_bn": "Delivery status check korchi...",
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
            "response_text_bn": "Apnar complaint er jonno ami apnake amader customer service agent er sathe connect korchi. Ektu oppokha korun.",
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
            "response_text_bn": "Ami apnar prosno ta thik bujhte parchi na. Ami apnake amader agent er sathe connect korchi.",
            "metadata": {
                "reason": "low_confidence",
                "priority": "normal"
            }
        }


# Singleton instance
dialogue_manager = DialogueManager()

