from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, UTC, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User
from app.services import PriceHistoryService
from app.schemas import (
    PriceHistoryPoint,
    PriceHistoryResponse,
)

router = APIRouter()


@router.get("/product/{product_id}/history", response_model=PriceHistoryResponse)
async def get_product_price_history(
    product_id: int,
    supermarket_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    service = PriceHistoryService()
    history = await service.get_price_history(product_id, supermarket_id, days, db)
    
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Build history points
    points = []
    for h in history:
        # Get supermarket name
        sm_result = await db.execute(select(Supermarket).where(Supermarket.id == h.supermarket_id))
        supermarket = sm_result.scalar_one_or_none()
        
        points.append(PriceHistoryPoint(
            date=h.recorded_at,
            price=h.price,
            original_price=h.original_price,
            is_promotion=h.is_promotion,
            supermarket_id=h.supermarket_id,
            supermarket_name=supermarket.name if supermarket else "Unknown",
        ))
    
    return PriceHistoryResponse(
        product_id=product_id,
        product_name=product.name,
        history=points,
        period_days=days,
    )