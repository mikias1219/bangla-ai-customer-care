from typing import Dict, Optional
import uuid
from datetime import datetime

from app.db.models import Client, ClientPayment, PaymentStatus


class PaymentService:
    """Payment processing service"""

    @staticmethod
    def calculate_plan_price(plan: str) -> float:
        """Calculate price for subscription plan"""
        prices = {
            "basic": 3999.0,      # Tk 3,999
            "standard": 7499.0,   # Tk 7,499
            "premium": 17999.0,   # Tk 17,999
            "pay_as_you_go": 0.75  # Tk 0.75 per reply
        }
        return prices.get(plan, 0.0)

    @staticmethod
    def process_subscription_payment(
        client: Client,
        plan: str,
        payment_method: str = "manual",
        gateway_data: Optional[Dict] = None
    ) -> ClientPayment:
        """Process subscription payment"""
        amount = PaymentService.calculate_plan_price(plan)

        payment = ClientPayment(
            client_id=client.id,
            transaction_id=f"sub_{uuid.uuid4().hex[:16]}",
            amount=amount,
            currency="BDT",
            payment_type="subscription",
            gateway=payment_method,
            gateway_transaction_id=gateway_data.get("transaction_id") if gateway_data else None,
            gateway_response=gateway_data,
            description=f"Subscription payment for {plan} plan",
            status=PaymentStatus.paid,
            paid_at=datetime.utcnow()
        )

        return payment

    @staticmethod
    def process_ai_reply_payment(
        client: Client,
        reply_count: int = 1,
        payment_method: str = "balance"
    ) -> ClientPayment:
        """Process payment for AI replies"""
        amount = reply_count * 0.75  # Tk 0.75 per reply

        payment = ClientPayment(
            client_id=client.id,
            transaction_id=f"ai_{uuid.uuid4().hex[:16]}",
            amount=amount,
            currency="BDT",
            payment_type="ai_reply",
            gateway=payment_method,
            description=f"AI reply payment for {reply_count} replies",
            status=PaymentStatus.paid,
            paid_at=datetime.utcnow()
        )

        return payment

    @staticmethod
    def check_client_balance(client: Client, required_replies: int = 1) -> bool:
        """Check if client has sufficient balance for AI replies"""
        required_amount = required_replies * 0.75
        return client.ai_reply_balance >= required_amount

    @staticmethod
    def deduct_ai_reply_balance(client: Client, reply_count: int = 1) -> float:
        """Deduct balance for AI replies"""
        deduction = reply_count * 0.75
        client.ai_reply_balance -= deduction
        return client.ai_reply_balance

    @staticmethod
    def topup_balance(
        client: Client,
        amount: float,
        payment_method: str = "manual",
        gateway_data: Optional[Dict] = None
    ) -> ClientPayment:
        """Top up client balance"""
        payment = ClientPayment(
            client_id=client.id,
            transaction_id=f"topup_{uuid.uuid4().hex[:16]}",
            amount=amount,
            currency="BDT",
            payment_type="topup",
            gateway=payment_method,
            gateway_transaction_id=gateway_data.get("transaction_id") if gateway_data else None,
            gateway_response=gateway_data,
            description=f"Balance topup of Tk {amount}",
            status=PaymentStatus.paid,
            paid_at=datetime.utcnow()
        )

        # Add to client balance
        client.ai_reply_balance += amount

        return payment


# bKash integration (simplified)
class BKashPaymentService:
    """bKash payment processing"""

    @staticmethod
    def create_payment_request(amount: float, client_id: int) -> Dict:
        """Create bKash payment request"""
        # In production, integrate with actual bKash API
        return {
            "payment_id": f"bkash_{uuid.uuid4().hex}",
            "amount": amount,
            "currency": "BDT",
            "status": "pending",
            "client_id": client_id,
            "redirect_url": f"https://checkout.bkash.com/{uuid.uuid4().hex}"
        }

    @staticmethod
    def verify_payment(payment_id: str) -> bool:
        """Verify bKash payment"""
        # In production, verify with bKash API
        return True


# Stripe integration (placeholder)
class StripePaymentService:
    """Stripe payment processing"""

    @staticmethod
    def create_payment_intent(amount: float, currency: str = "bdt") -> Dict:
        """Create Stripe payment intent"""
        # In production, integrate with Stripe API
        return {
            "client_secret": f"pi_{uuid.uuid4().hex}_secret_{uuid.uuid4().hex}",
            "amount": amount,
            "currency": currency
        }

    @staticmethod
    def confirm_payment(payment_intent_id: str) -> bool:
        """Confirm Stripe payment"""
        # In production, confirm with Stripe API
        return True
