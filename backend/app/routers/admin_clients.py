from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import jwt
import bcrypt

from app.core.config import settings
from app.core.tenant import TenantContext
from app.db.session import get_admin_db
from app.db.models import (
    Client, ClientUser, Subscription, ClientPayment,
    SubscriptionPlan, ClientStatus, PaymentStatus
)


router = APIRouter()
security = HTTPBearer()


# Pydantic models
class ClientCreate(BaseModel):
    business_name: str
    business_email: EmailStr
    business_phone: Optional[str] = None
    business_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    website_url: Optional[str] = None
    facebook_page_url: Optional[str] = None
    instagram_username: Optional[str] = None
    subscription_plan: SubscriptionPlan = SubscriptionPlan.pay_as_you_go
    language_preference: str = "bn"


class ClientUpdate(BaseModel):
    business_name: Optional[str] = None
    business_email: Optional[EmailStr] = None
    business_phone: Optional[str] = None
    business_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    website_url: Optional[str] = None
    facebook_page_url: Optional[str] = None
    instagram_username: Optional[str] = None
    status: Optional[ClientStatus] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    language_preference: Optional[str] = None


class ClientUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "admin"


class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan
    amount: float
    currency: str = "BDT"
    auto_renew: bool = True


class ClientResponse(BaseModel):
    id: int
    tenant_id: str
    business_name: str
    business_email: str
    business_phone: Optional[str]
    business_address: Optional[str]
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    business_type: Optional[str]
    website_url: Optional[str]
    facebook_page_url: Optional[str]
    instagram_username: Optional[str]
    status: ClientStatus
    subscription_plan: SubscriptionPlan
    monthly_customers_limit: Optional[int]
    current_month_customers: Optional[int]
    ai_reply_balance: Optional[float]
    language_preference: str
    trial_started_at: Optional[datetime]
    subscription_started_at: Optional[datetime]
    subscription_renewal_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class ClientUserResponse(BaseModel):
    id: int
    client_id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


# Admin authentication (simplified - in production, use proper admin user management)
def get_admin_token():
    """Simple admin token validation - in production, use proper admin authentication"""
    return "admin_token_2024"  # Replace with proper admin authentication


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token"""
    if credentials.credentials != get_admin_token():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token"
        )
    return True


@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Create a new client/tenant"""
    # Check if email already exists
    existing_client = db.query(Client).filter(Client.business_email == client_data.business_email).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Client with this email already exists")

    # Set default limits based on plan
    monthly_limit = {
        SubscriptionPlan.basic: 500,
        SubscriptionPlan.standard: 1000,
        SubscriptionPlan.premium: 2500,
        SubscriptionPlan.pay_as_you_go: 100
    }.get(client_data.subscription_plan, 100)

    ai_balance = {
        SubscriptionPlan.basic: 500.0,
        SubscriptionPlan.standard: 1000.0,
        SubscriptionPlan.premium: 2500.0,
        SubscriptionPlan.pay_as_you_go: 500.0
    }.get(client_data.subscription_plan, 500.0)

    # Create client
    client = Client(
        business_name=client_data.business_name,
        business_email=client_data.business_email,
        business_phone=client_data.business_phone,
        business_address=client_data.business_address,
        contact_person=client_data.contact_person,
        contact_email=client_data.contact_email,
        contact_phone=client_data.contact_phone,
        business_type=client_data.business_type,
        website_url=client_data.website_url,
        facebook_page_url=client_data.facebook_page_url,
        instagram_username=client_data.instagram_username,
        subscription_plan=client_data.subscription_plan,
        monthly_customers_limit=monthly_limit,
        ai_reply_balance=ai_balance,
        language_preference=client_data.language_preference,
        status=ClientStatus.trial
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return ClientResponse(**client.__dict__)


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ClientStatus] = None,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """List all clients"""
    query = db.query(Client)
    if status_filter:
        query = query.filter(Client.status == status_filter)

    clients = query.offset(skip).limit(limit).all()
    return [ClientResponse(**client.__dict__) for client in clients]


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Get client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return ClientResponse(**client.__dict__)


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Update client information"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    # Update limits if plan changed
    if 'subscription_plan' in update_data:
        plan = update_data['subscription_plan']
        monthly_limit = {
            SubscriptionPlan.basic: 500,
            SubscriptionPlan.standard: 1000,
            SubscriptionPlan.premium: 2500,
            SubscriptionPlan.pay_as_you_go: 100
        }.get(plan, 100)

        ai_balance = {
            SubscriptionPlan.basic: 500.0,
            SubscriptionPlan.standard: 1000.0,
            SubscriptionPlan.premium: 2500.0,
            SubscriptionPlan.pay_as_you_go: 500.0
        }.get(plan, 500.0)

        client.monthly_customers_limit = monthly_limit
        client.ai_reply_balance = ai_balance

    db.commit()
    db.refresh(client)

    return ClientResponse(**client.__dict__)


@router.post("/clients/{client_id}/users", response_model=ClientUserResponse)
async def create_client_user(
    client_id: int,
    user_data: ClientUserCreate,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Create a user for a client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if username or email already exists
    existing_user = db.query(ClientUser).filter(
        (ClientUser.username == user_data.username) |
        (ClientUser.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create user
    user = ClientUser(
        client_id=client_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return ClientUserResponse(**user.__dict__)


@router.get("/clients/{client_id}/users", response_model=List[ClientUserResponse])
async def list_client_users(
    client_id: int,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """List users for a client"""
    users = db.query(ClientUser).filter(ClientUser.client_id == client_id).all()
    return [ClientUserResponse(**user.__dict__) for user in users]


@router.post("/clients/{client_id}/subscriptions", response_model=dict)
async def create_subscription(
    client_id: int,
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Create a subscription for a client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Create subscription
    subscription = Subscription(
        client_id=client_id,
        plan=subscription_data.plan,
        amount=subscription_data.amount,
        currency=subscription_data.currency,
        auto_renew=subscription_data.auto_renew
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return {"message": "Subscription created successfully", "subscription_id": subscription.id}


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    db: Session = Depends(get_admin_db),
    _: bool = Depends(verify_admin_token)
):
    """Delete a client (soft delete by setting status to inactive)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.status = ClientStatus.inactive
    db.commit()

    return {"message": "Client deactivated successfully"}
