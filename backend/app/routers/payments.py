from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.core.tenant import get_current_tenant, TenantContext
from app.db.session import get_admin_db
from app.db.models import Client, ClientPayment, PaymentStatus
from app.services.payment_service import PaymentService, BKashPaymentService, StripePaymentService


router = APIRouter()


class PaymentCreate(BaseModel):
    amount: float
    payment_type: str  # subscription, topup, ai_reply
    gateway: str = "manual"  # bkash, stripe, manual
    description: Optional[str] = None


class TopupRequest(BaseModel):
    amount: float
    gateway: str = "bkash"  # bkash, stripe


class PaymentResponse(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    payment_type: str
    status: PaymentStatus
    gateway: str
    description: Optional[str]
    paid_at: Optional[str]


@router.post("/topup", response_model=dict)
async def request_topup(
    topup_data: TopupRequest,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Request balance topup"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if topup_data.gateway == "bkash":
        # Create bKash payment request
        bkash_payment = BKashPaymentService.create_payment_request(
            topup_data.amount, client_id
        )
        return {
            "gateway": "bkash",
            "payment_url": bkash_payment["redirect_url"],
            "payment_id": bkash_payment["payment_id"],
            "amount": topup_data.amount
        }

    elif topup_data.gateway == "stripe":
        # Create Stripe payment intent
        stripe_payment = StripePaymentService.create_payment_intent(
            topup_data.amount * 100, "bdt"  # Convert to paisa
        )
        return {
            "gateway": "stripe",
            "client_secret": stripe_payment["client_secret"],
            "amount": topup_data.amount
        }

    else:
        raise HTTPException(status_code=400, detail="Unsupported payment gateway")


@router.post("/topup/confirm", response_model=PaymentResponse)
async def confirm_topup(
    payment_id: str,
    gateway: str,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Confirm topup payment"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Verify payment
    payment_verified = False
    if gateway == "bkash":
        payment_verified = BKashPaymentService.verify_payment(payment_id)
    elif gateway == "stripe":
        payment_verified = StripePaymentService.confirm_payment(payment_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment gateway")

    if not payment_verified:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    # Get amount from payment gateway (in production, get from gateway response)
    amount = 1000.0  # This should come from gateway callback/webhook

    # Process topup
    payment = PaymentService.topup_balance(
        client, amount, gateway,
        {"transaction_id": payment_id}
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        transaction_id=payment.transaction_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_type=payment.payment_type,
        status=payment.status,
        gateway=payment.gateway,
        description=payment.description,
        paid_at=payment.paid_at.isoformat() if payment.paid_at else None
    )


@router.get("/balance")
async def get_balance(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Get current balance"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "ai_reply_balance": client.ai_reply_balance,
        "subscription_plan": client.subscription_plan,
        "monthly_customers_limit": client.monthly_customers_limit,
        "current_month_customers": client.current_month_customers
    }


@router.get("/transactions", response_model=list[PaymentResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 50,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Get payment transactions"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payments = db.query(ClientPayment).filter(
        ClientPayment.client_id == client_id
    ).order_by(ClientPayment.created_at.desc()).offset(skip).limit(limit).all()

    return [
        PaymentResponse(
            transaction_id=payment.transaction_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_type=payment.payment_type,
            status=payment.status,
            gateway=payment.gateway,
            description=payment.description,
            paid_at=payment.paid_at.isoformat() if payment.paid_at else None
        )
        for payment in payments
    ]


# Admin endpoints
@router.post("/admin/process-payment", response_model=PaymentResponse)
async def process_manual_payment(
    client_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_admin_db)
):
    """Admin: Process manual payment"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Create payment record
    payment = ClientPayment(
        client_id=client_id,
        transaction_id=f"manual_{uuid.uuid4().hex[:16]}",
        amount=payment_data.amount,
        currency="BDT",
        payment_type=payment_data.payment_type,
        gateway=payment_data.gateway,
        description=payment_data.description or f"Manual payment",
        status=PaymentStatus.paid,
        paid_at=datetime.utcnow()
    )

    # Update client balance if it's a topup
    if payment_data.payment_type == "topup":
        client.ai_reply_balance += payment_data.amount

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        transaction_id=payment.transaction_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_type=payment.payment_type,
        status=payment.status,
        gateway=payment.gateway,
        description=payment.description,
        paid_at=payment.paid_at.isoformat() if payment.paid_at else None
    )
