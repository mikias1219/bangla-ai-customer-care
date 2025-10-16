from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import bcrypt

from app.db.session import get_admin_db
from app.db.models import Client, ClientUser, ClientStatus, SubscriptionPlan
from app.services.payment_service import PaymentService

router = APIRouter()


class ClientRegistration(BaseModel):
    business_name: str
    business_email: EmailStr
    business_phone: str
    business_address: str
    contact_person: str
    contact_email: EmailStr
    contact_phone: str
    business_type: str
    website_url: str = ""
    facebook_page_url: str = ""
    instagram_username: str = ""
    password: str
    subscription_plan: SubscriptionPlan = SubscriptionPlan.pay_as_you_go
    language_preference: str = "bn"


class RegistrationResponse(BaseModel):
    message: str
    tenant_id: str
    client_id: int
    trial_days: int = 7


@router.post("/register", response_model=RegistrationResponse)
async def register_client(
    registration_data: ClientRegistration,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_admin_db)
):
    """Public client registration endpoint"""

    # Check if email already exists
    existing_client = db.query(Client).filter(Client.business_email == registration_data.business_email).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Business email already registered")

    # Generate tenant ID
    tenant_id = str(uuid.uuid4())

    # Hash password
    hashed_password = bcrypt.hashpw(registration_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Set default limits based on plan
    monthly_limit = {
        SubscriptionPlan.basic: 500,
        SubscriptionPlan.standard: 1000,
        SubscriptionPlan.premium: 2500,
        SubscriptionPlan.pay_as_you_go: 100
    }.get(registration_data.subscription_plan, 100)

    ai_balance = {
        SubscriptionPlan.basic: 500.0,
        SubscriptionPlan.standard: 1000.0,
        SubscriptionPlan.premium: 2500.0,
        SubscriptionPlan.pay_as_you_go: 500.0  # Free trial balance
    }.get(registration_data.subscription_plan, 500.0)

    # Create client
    client = Client(
        tenant_id=tenant_id,
        business_name=registration_data.business_name,
        business_email=registration_data.business_email,
        business_phone=registration_data.business_phone,
        business_address=registration_data.business_address,
        contact_person=registration_data.contact_person,
        contact_email=registration_data.contact_email,
        contact_phone=registration_data.contact_phone,
        business_type=registration_data.business_type,
        website_url=registration_data.website_url,
        facebook_page_url=registration_data.facebook_page_url,
        instagram_username=registration_data.instagram_username,
        subscription_plan=registration_data.subscription_plan,
        monthly_customers_limit=monthly_limit,
        ai_reply_balance=ai_balance,
        language_preference=registration_data.language_preference,
        status=ClientStatus.trial
    )

    db.add(client)
    db.flush()  # Get client ID

    # Create admin user for the client
    admin_user = ClientUser(
        client_id=client.id,
        username=registration_data.business_email.split('@')[0],  # Use email prefix as username
        email=registration_data.business_email,
        hashed_password=hashed_password,
        full_name=registration_data.contact_person,
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    db.refresh(client)

    # Send welcome email (background task)
    background_tasks.add_task(send_welcome_email, client, admin_user)

    return RegistrationResponse(
        message="Registration successful! Welcome to Bangla AI platform.",
        tenant_id=tenant_id,
        client_id=client.id,
        trial_days=7
    )


async def send_welcome_email(client: Client, user: ClientUser):
    """Send welcome email to new client"""
    # In production, integrate with email service like SendGrid, Mailgun, etc.
    print(f"""
    Welcome Email to: {client.business_email}

    Subject: Welcome to Bangla AI - Your AI Business Assistant!

    Dear {client.contact_person},

    Welcome to Bangla AI! Your account has been successfully created.

    Business Details:
    - Business Name: {client.business_name}
    - Tenant ID: {client.tenant_id}
    - Plan: {client.subscription_plan.value}

    Login Credentials:
    - Email: {user.email}
    - You can login at: https://app.bangla.ai/login

    Your 7-day free trial has started. You have ৳{client.ai_reply_balance} credit to get started.

    Next Steps:
    1. Login to your dashboard
    2. Connect your Facebook/Instagram pages
    3. Train your AI assistant with your business information
    4. Start responding to customer messages automatically!

    Need help? Contact us at support@bangla.ai

    Best regards,
    The Bangla AI Team
    """)


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "pay_as_you_go",
                "name": "Pay as You Go",
                "price": 0.75,
                "currency": "BDT",
                "billing": "per AI reply",
                "features": [
                    "Pay only for what you use",
                    "No monthly commitment",
                    "500 replies free trial",
                    "24/7 customer support"
                ]
            },
            {
                "id": "basic",
                "name": "Basic",
                "price": 3999,
                "currency": "BDT",
                "billing": "per month",
                "features": [
                    "Up to 500 customers/month",
                    "Instant replies",
                    "Facebook & Instagram integration",
                    "Basic reporting",
                    "Email support"
                ]
            },
            {
                "id": "standard",
                "name": "Standard",
                "price": 7499,
                "currency": "BDT",
                "billing": "per month",
                "features": [
                    "Up to 1000 customers/month",
                    "All Basic features",
                    "Advanced AI training",
                    "Order management",
                    "Priority support"
                ]
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": 17999,
                "currency": "BDT",
                "billing": "per month",
                "features": [
                    "Up to 2500 customers/month",
                    "All Standard features",
                    "Multi-language support",
                    "Custom integrations",
                    "Dedicated account manager"
                ]
            }
        ]
    }
