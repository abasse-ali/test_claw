from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from math import radians, cos, sin, acos

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.supermarket import Supermarket
from app.models.user import User
from app.schemas import (
    SupermarketCreate,
    SupermarketUpdate,
    SupermarketResponse,
    SupermarketWithPrices,
    PaginatedResponse,
)

router = APIRouter()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two points using Haversine formula."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * acos(min(1, max(-1, a)))


@router.get("/nearby", response_model=list[SupermarketWithPrices])
async def get_nearby_supermarkets(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=10, gt=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Supermarket).where(Supermarket.is_active == True))
    supermarkets = result.scalars().all()

    nearby = []
    for sm in supermarkets:
        if sm.latitude and sm.longitude:
            dist = haversine_distance(lat, lon, sm.latitude, sm.longitude)
            if dist <= radius_km:
                sm_dict = SupermarketWithPrices.model_validate(sm)
                sm_dict.distance_km = round(dist, 2)
                nearby.append(sm_dict)

    nearby.sort(key=lambda x: x.distance_km or 999)
    return nearby


@router.get("", response_model=PaginatedResponse)
async def list_supermarkets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Supermarket)
    if city:
        query = query.where(Supermarket.city.ilike(f"%{city}%"))
    if brand:
        query = query.where(Supermarket.brand.ilike(f"%{brand}%"))
    if is_active is not None:
        query = query.where(Supermarket.is_active == is_active)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    supermarkets = result.scalars().all()

    return {
        "items": [SupermarketResponse.model_validate(sm) for sm in supermarkets],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=SupermarketResponse, status_code=201)
async def create_supermarket(
    sm_in: SupermarketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    sm = Supermarket(**sm_in.model_dump())
    db.add(sm)
    await db.commit()
    await db.refresh(sm)
    return sm


@router.get("/{sm_id}", response_model=SupermarketResponse)
async def get_supermarket(sm_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supermarket).where(Supermarket.id == sm_id))
    sm = result.scalar_one_or_none()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    return sm


@router.patch("/{sm_id}", response_model=SupermarketResponse)
async def update_supermarket(
    sm_id: int,
    sm_update: SupermarketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(Supermarket).where(Supermarket.id == sm_id))
    sm = result.scalar_one_or_none()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")

    for field, value in sm_update.model_dump(exclude_unset=True).items():
        setattr(sm, field, value)

    await db.commit()
    await db.refresh(sm)
    return sm


@router.delete("/{sm_id}", status_code=204)
async def delete_supermarket(
    sm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(Supermarket).where(Supermarket.id == sm_id))
    sm = result.scalar_one_or_none()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")

    await db.delete(sm)
    await db.commit()