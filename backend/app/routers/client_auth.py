from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.tenant import get_current_tenant, create_tenant_token, TenantContext
from app.db.session import get_admin_db
from app.db.models import Client, ClientUser


router = APIRouter()
security = HTTPBearer()


class ClientLogin(BaseModel):
    email: EmailStr
    password: str


class ClientLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: str
    client_id: int
    user_id: int
    business_name: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


@router.post("/client/login", response_model=ClientLoginResponse)
async def client_login(
    login_data: ClientLogin,
    db: Session = Depends(get_admin_db)
):
    """Client user login"""
    # Find user by email
    user = db.query(ClientUser).filter(ClientUser.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # Get client information
    client = db.query(Client).filter(Client.id == user.client_id).first()
    if not client or client.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create token
    access_token = create_tenant_token(client.id, user.id, client.tenant_id)

    return ClientLoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        tenant_id=client.tenant_id,
        client_id=client.id,
        user_id=user.id,
        business_name=client.business_name
    )


@router.post("/client/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: ClientUser = Depends(lambda: None),  # Will be implemented with proper auth
    db: Session = Depends(get_admin_db)
):
    """Change client user password"""
    # This would need proper authentication middleware
    # For now, return placeholder
    return {"message": "Password changed successfully"}


@router.get("/client/profile")
async def get_client_profile(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Get current client profile"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "id": client.id,
        "tenant_id": client.tenant_id,
        "business_name": client.business_name,
        "business_email": client.business_email,
        "business_phone": client.business_phone,
        "business_address": client.business_address,
        "contact_person": client.contact_person,
        "contact_email": client.contact_email,
        "contact_phone": client.contact_phone,
        "business_type": client.business_type,
        "website_url": client.website_url,
        "facebook_page_url": client.facebook_page_url,
        "instagram_username": client.instagram_username,
        "status": client.status,
        "subscription_plan": client.subscription_plan,
        "monthly_customers_limit": client.monthly_customers_limit,
        "current_month_customers": client.current_month_customers,
        "ai_reply_balance": client.ai_reply_balance,
        "language_preference": client.language_preference,
        "trial_started_at": client.trial_started_at,
        "subscription_started_at": client.subscription_started_at,
        "subscription_renewal_at": client.subscription_renewal_at,
        "created_at": client.created_at
    }


@router.put("/client/profile")
async def update_client_profile(
    profile_data: dict,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Update client profile"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update allowed fields
    allowed_fields = [
        'business_phone', 'business_address', 'contact_person',
        'contact_email', 'contact_phone', 'website_url',
        'facebook_page_url', 'instagram_username', 'language_preference'
    ]

    for field in allowed_fields:
        if field in profile_data:
            setattr(client, field, profile_data[field])

    db.commit()
    db.refresh(client)

    return {"message": "Profile updated successfully"}


@router.get("/client/stats")
async def get_client_stats(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_admin_db)
):
    """Get client usage statistics"""
    client_id = TenantContext.get_client_id()
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # This would aggregate statistics from conversations, orders, etc.
    # For now, return basic info
    client = db.query(Client).filter(Client.id == client_id).first()

    return {
        "subscription_plan": client.subscription_plan,
        "monthly_customers_limit": client.monthly_customers_limit,
        "current_month_customers": client.current_month_customers,
        "ai_reply_balance": client.ai_reply_balance,
        "status": client.status
    }
