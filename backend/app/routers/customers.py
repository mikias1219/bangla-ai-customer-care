from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.base import get_db
from app.db.models import Customer, Order

router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerBase(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    channel: str = Field(..., max_length=50)  # whatsapp, messenger, instagram, etc.
    channel_user_id: str = Field(..., max_length=100)
    profile_data: Optional[dict] = None
    preferences: Optional[dict] = None
    tags: Optional[List[str]] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    profile_data: Optional[dict] = None
    preferences: Optional[dict] = None
    tags: Optional[List[str]] = None


class CustomerResponse(CustomerBase):
    id: int
    total_orders: int
    total_spent: float
    last_order_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if customer_id already exists
    existing_customer = db.query(Customer).filter(Customer.customer_id == customer.customer_id).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this ID already exists")

    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    channel: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List customers with filtering and pagination"""
    query = db.query(Customer)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.phone.ilike(search_term),
                Customer.customer_id.ilike(search_term)
            )
        )

    if channel:
        query = query.filter(Customer.channel == channel)

    if email:
        query = query.filter(Customer.email == email)

    if phone:
        query = query.filter(Customer.phone == phone)

    # Order by creation date (newest first)
    query = query.order_by(Customer.created_at.desc())

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/by-external-id/{external_id}", response_model=CustomerResponse)
def get_customer_by_external_id(external_id: str, db: Session = Depends(get_db)):
    """Get a customer by external ID (from channels)"""
    customer = db.query(Customer).filter(Customer.customer_id == external_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Update fields
    for field, value in customer_update.dict(exclude_unset=True).items():
        setattr(customer, field, value)

    customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if customer has orders
    order_count = db.query(Order).filter(Order.customer_id == customer_id).count()
    if order_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete customer that has {order_count} order(s)"
        )

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


@router.get("/{customer_id}/orders")
def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get orders for a specific customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    orders = db.query(Order).options(joinedload(Order.items)).filter(
        Order.customer_id == customer_id
    ).order_by(Order.ordered_at.desc()).offset(skip).limit(limit).all()

    return orders


@router.get("/channels", response_model=List[str])
def get_customer_channels(db: Session = Depends(get_db)):
    """Get all unique customer channels"""
    result = db.query(Customer.channel).filter(
        and_(Customer.channel.isnot(None), Customer.channel != "")
    ).distinct().all()
    return [channel[0] for channel in result]


@router.get("/stats/overview")
def get_customer_stats(db: Session = Depends(get_db)):
    """Get customer statistics overview"""
    total_customers = db.query(Customer).count()

    # Channel distribution
    channel_stats = db.query(
        Customer.channel,
        func.count(Customer.id).label('count')
    ).group_by(Customer.channel).all()

    channel_distribution = {channel: count for channel, count in channel_stats}

    # Customer with orders
    customers_with_orders = db.query(Customer).filter(Customer.total_orders > 0).count()

    return {
        "total_customers": total_customers,
        "channel_distribution": channel_distribution,
        "customers_with_orders": customers_with_orders,
        "customers_without_orders": total_customers - customers_with_orders
    }
