from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithPrices,
    ProductSearchParams,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/search", response_model=PaginatedResponse)
async def search_products(
    q: Optional[str] = Query(None, alias="query"),
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    barcode: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    supermarket_id: Optional[int] = None,
    city: Optional[str] = None,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(default=10, gt=0, le=100),
    is_promotion: Optional[bool] = None,
    in_stock_only: bool = True,
    sort_by: str = Query("price_asc", pattern="^(price_asc|price_desc|relevance|newest)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Placeholder - full implementation in M2
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0,
    }


@router.get("", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    return {
        "items": [ProductResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    prod_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    prod = Product(**prod_in.model_dump())
    db.add(prod)
    await db.commit()
    await db.refresh(prod)
    return prod


@router.get("/{prod_id}", response_model=ProductWithPrices)
async def get_product(prod_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == prod_id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@router.patch("/{prod_id}", response_model=ProductResponse)
async def update_product(
    prod_id: int,
    prod_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(Product).where(Product.id == prod_id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in prod_update.model_dump(exclude_unset=True).items():
        setattr(prod, field, value)

    await db.commit()
    await db.refresh(prod)
    return prod