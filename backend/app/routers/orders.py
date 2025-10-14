from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.db.base import get_db
from app.db.models import Order, OrderItem, Customer, Product, Transaction, OrderStatus, PaymentStatus

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    product_options: Optional[dict] = None
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    customer_id: int
    conversation_id: Optional[int] = None
    items: List[OrderItemBase] = Field(..., min_items=1)
    currency: str = Field(default="BDT", max_length=10)
    shipping_address: Optional[dict] = None
    shipping_method: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    shipping_address: Optional[dict] = None
    shipping_method: Optional[str] = Field(None, max_length=100)
    tracking_number: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    payment_gateway: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: float
    total_price: float
    product_options: Optional[dict]
    notes: Optional[str]

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    conversation_id: Optional[int]
    status: OrderStatus
    payment_status: PaymentStatus
    currency: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    shipping_amount: float
    total_amount: float
    shipping_address: Optional[dict]
    shipping_method: Optional[str]
    tracking_number: Optional[str]
    payment_method: Optional[str]
    payment_reference: Optional[str]
    payment_gateway: Optional[str]
    ordered_at: datetime
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    notes: Optional[str]
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify all products exist and are active
    product_ids = [item.product_id for item in order_data.items]
    products = db.query(Product).filter(
        and_(Product.id.in_(product_ids), Product.is_active == True)
    ).all()

    if len(products) != len(product_ids):
        found_ids = {p.id for p in products}
        missing_ids = set(product_ids) - found_ids
        raise HTTPException(
            status_code=400,
            detail=f"Products not found or inactive: {list(missing_ids)}"
        )

    # Create product lookup
    product_lookup = {p.id: p for p in products}

    # Calculate totals
    subtotal = 0
    for item in order_data.items:
        product = product_lookup[item.product_id]
        # Override unit_price if provided, otherwise use product price
        unit_price = item.unit_price if item.unit_price else product.price
        subtotal += unit_price * item.quantity

    tax_amount = 0.0  # Could implement tax calculation logic
    discount_amount = 0.0  # Could implement discount logic
    shipping_amount = 0.0  # Could implement shipping calculation logic
    total_amount = subtotal + tax_amount + shipping_amount - discount_amount

    # Generate order number
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Create order
    db_order = Order(
        order_number=order_number,
        customer_id=order_data.customer_id,
        conversation_id=order_data.conversation_id,
        currency=order_data.currency,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        shipping_method=order_data.shipping_method,
        payment_method=order_data.payment_method,
        notes=order_data.notes
    )

    db.add(db_order)
    db.flush()  # Get order ID

    # Create order items
    for item in order_data.items:
        product = product_lookup[item.product_id]
        unit_price = item.unit_price if item.unit_price else product.price
        total_price = unit_price * item.quantity

        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=product.name,
            product_sku=product.sku,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=total_price,
            product_options=item.product_options,
            notes=item.notes
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    # Load items for response
    db_order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == db_order.id).first()

    return db_order


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    customer_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    payment_status: Optional[PaymentStatus] = None,
    order_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List orders with filtering and pagination"""
    query = db.query(Order).options(joinedload(Order.items))

    # Apply filters
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    if status:
        query = query.filter(Order.status == status)

    if payment_status:
        query = query.filter(Order.payment_status == payment_status)

    if order_number:
        query = query.filter(Order.order_number.ilike(f"%{order_number}%"))

    # Order by creation date (newest first)
    query = query.order_by(Order.ordered_at.desc())

    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status timestamps
    if order_update.status and order_update.status != order.status:
        if order_update.status == OrderStatus.confirmed:
            order.confirmed_at = datetime.utcnow()
        elif order_update.status == OrderStatus.shipped:
            order.shipped_at = datetime.utcnow()
        elif order_update.status == OrderStatus.delivered:
            order.delivered_at = datetime.utcnow()
        elif order_update.status == OrderStatus.cancelled:
            order.cancelled_at = datetime.utcnow()

    # Update fields
    for field, value in order_update.dict(exclude_unset=True).items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)

    # Load items for response
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    return order


@router.get("/by-number/{order_number}", response_model=OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get an order by order number"""
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/stats/overview")
def get_order_stats(db: Session = Depends(get_db)):
    """Get order statistics overview"""
    total_orders = db.query(Order).count()
    total_revenue = db.query(Order).filter(Order.payment_status == PaymentStatus.paid).with_entities(
        db.func.sum(Order.total_amount)
    ).scalar() or 0.0

    pending_orders = db.query(Order).filter(Order.status.in_([OrderStatus.pending, OrderStatus.confirmed])).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.shipped).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.delivered).count()

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders
    }
