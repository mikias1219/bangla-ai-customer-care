"""
NLU Service for Bangla intent classification and entity extraction
Uses BanglaBERT/IndicBERT for intent classification
"""
from typing import Dict, Any, List, Optional
import re
AutoTokenizer = None
AutoModelForSequenceClassification = None
torch = None

from app.core.config import settings


class NLUService:
    def __init__(self):
        self.model_name = settings.nlu_model_name
        self.tokenizer = None
        self.model = None
        self.intent_labels = [
            "order_status",
            "return_request",
            "product_inquiry",
            "payment_issue",
            "delivery_tracking",
            "complaint",
            "fallback"
        ]
        
    def load_model(self):
        """Load the NLU model (lazy). Falls back to keyword rules if unavailable."""
        global AutoTokenizer, AutoModelForSequenceClassification, torch
        if self.model is None:
            try:
                if AutoTokenizer is None:
                    from transformers import AutoTokenizer as _AT, AutoModelForSequenceClassification as _AM
                    AutoTokenizer = _AT
                    AutoModelForSequenceClassification = _AM
                import torch as _torch
                torch = _torch
                print(f"Loading NLU model: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=len(self.intent_labels)
                )
                self.model.eval()
            except Exception as e:
                print(f"Transformers not available, using keyword-based NLU: {e}")
                self.model = "rules"
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using regex patterns
        In production, use a trained NER model or spaCy
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
        amount_pattern = r'(?:৳|টাকা|taka|tk)\s*(\d+)'
        amount_match = re.search(amount_pattern, text, re.IGNORECASE)
        if amount_match:
            entities['amount'] = amount_match.group(1)
        
        return entities
    
    def classify_intent(self, text: str) -> tuple[str, float]:
        """
        Classify intent using the loaded model
        Returns (intent, confidence)
        """
        # Simple keyword-based classification for now
        # In production, use the fine-tuned transformer model
        text_lower = text.lower()
        
        keywords = {
            "order_status": ["order", "অর্ডার", "status", "কোথায়", "kothay"],
            "return_request": ["return", "রিটার্ন", "ফেরত", "ferot"],
            "product_inquiry": ["product", "প্রোডাক্ট", "available", "আছে"],
            "payment_issue": ["payment", "পেমেন্ট", "টাকা", "taka"],
            "delivery_tracking": ["delivery", "ডেলিভারি", "courier", "কুরিয়ার"],
            "complaint": ["complaint", "অভিযোগ", "problem", "সমস্যা"]
        }
        
        scores = {}
        for intent, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[intent] = score
        
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(0.9, 0.5 + scores[best_intent] * 0.1)
            return best_intent, confidence
        
        return "fallback", 0.3
    
    def resolve(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main NLU resolution method
        """
        intent, confidence = self.classify_intent(text)
        entities = self.extract_entities(text)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "text": text
        }


# Singleton instance
nlu_service = NLUService()

