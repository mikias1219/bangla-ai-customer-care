from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.db.base import get_db
from app.db.models import Product, OrderItem
from app.core.config import settings

router = APIRouter(prefix="/products", tags=["products"])


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    currency: str = Field(default="BDT", max_length=10)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock_level: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[dict] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = Field(default=None, alias="product_metadata")


class ProductCreate(ProductBase):
    model_config = ConfigDict(populate_by_name=True)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=10)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[dict] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = Field(default=None, alias="product_metadata")

    model_config = ConfigDict(populate_by_name=True)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List products with filtering and pagination"""
    query = db.query(Product)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.category.ilike(search_term),
                Product.brand.ilike(search_term)
            )
        )

    if category:
        query = query.filter(Product.category == category)

    if brand:
        query = query.filter(Product.brand == brand)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Order by creation date (newest first)
    query = query.order_by(Product.created_at.desc())

    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if SKU is being changed and if it conflicts
    if product_update.sku and product_update.sku != product.sku:
        existing_product = db.query(Product).filter(
            and_(Product.sku == product_update.sku, Product.id != product_id)
        ).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    # Update fields
    for field, value in product_update.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if product has order items
    order_count = db.query(OrderItem).filter(OrderItem.product_id == product_id).count()
    if order_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete product that has {order_count} order(s). Deactivate it instead."
        )

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


@router.get("/inventory/low-stock", response_model=List[ProductResponse])
def get_low_stock_products(db: Session = Depends(get_db)):
    """Get products with low stock (below minimum stock level)"""
    products = db.query(Product).filter(
        and_(
            Product.is_active == True,
            Product.stock_quantity <= Product.min_stock_level
        )
    ).all()
    return products


@router.get("/categories", response_model=List[str])
def get_product_categories(db: Session = Depends(get_db)):
    """Get all unique product categories"""
    result = db.query(Product.category).filter(
        and_(Product.category.isnot(None), Product.category != "")
    ).distinct().all()
    return [category[0] for category in result]


@router.get("/brands", response_model=List[str])
def get_product_brands(db: Session = Depends(get_db)):
    """Get all unique product brands"""
    result = db.query(Product.brand).filter(
        and_(Product.brand.isnot(None), Product.brand != "")
    ).distinct().all()
    return [brand[0] for brand in result]
