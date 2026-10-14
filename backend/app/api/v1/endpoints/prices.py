from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.price import Price
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User
from app.services import PriceService
from app.schemas import (
    PriceCreate,
    PriceUpdate,
    PriceResponse,
    PriceComparisonResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_prices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    supermarket_id: Optional[int] = None,
    is_promotion: Optional[bool] = None,
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Price)
    if product_id:
        query = query.where(Price.product_id == product_id)
    if supermarket_id:
        query = query.where(Price.supermarket_id == supermarket_id)
    if is_promotion is not None:
        query = query.where(Price.is_promotion == is_promotion)
    if is_available is not None:
        query = query.where(Price.is_available == is_available)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(Price.scraped_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    prices = result.scalars().all()

    return {
        "items": [PriceResponse.model_validate(p) for p in prices],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=PriceResponse, status_code=201)
async def create_price(
    price_in: PriceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    # Verify product and supermarket exist
    for model, id_val in [(Product, price_in.product_id), (Supermarket, price_in.supermarket_id)]:
        result = await db.execute(select(model).where(model.id == id_val))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

    price = Price(**price_in.model_dump())
    db.add(price)
    
    # Create price history
    from app.models.price_history import PriceHistory
    history = PriceHistory(
        product_id=price_in.product_id,
        supermarket_id=price_in.supermarket_id,
        price=price_in.price,
        original_price=price_in.original_price,
        is_promotion=price_in.is_promotion,
        recorded_at=price_in.scraped_at,
    )
    db.add(history)

    await db.commit()
    await db.refresh(price)
    return price


@router.get("/product/{product_id}/comparison", response_model=PriceComparisonResponse)
async def compare_product_prices(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = PriceService()
    comparison = await service.get_price_comparison(product_id, db)
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return PriceComparisonResponse(
        product=comparison["product"],
        prices=comparison["prices"],
        cheapest=comparison["cheapest"],
        most_expensive=comparison["most_expensive"],
        average_price=comparison["average_price"],
        price_spread=comparison["price_spread"],
    )