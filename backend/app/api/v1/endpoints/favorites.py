from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user_favorite import UserFavorite
from app.models.user_favorite_supermarket import UserFavoriteSupermarket
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User
from app.schemas import (
    UserFavoriteCreate,
    UserFavoriteResponse,
    UserFavoriteSupermarketCreate,
    UserFavoriteSupermarketResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/products", response_model=PaginatedResponse)
async def list_favorite_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(UserFavorite).where(UserFavorite.user_id == current_user.id)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    favorites = result.scalars().all()

    return {
        "items": [UserFavoriteResponse.model_validate(f) for f in favorites],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/products", response_model=UserFavoriteResponse, status_code=201)
async def add_favorite_product(
    fav_in: UserFavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == fav_in.product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    # Check duplicate
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.product_id == fav_in.product_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in favorites")

    fav = UserFavorite(user_id=current_user.id, product_id=fav_in.product_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.delete("/products/{product_id}", status_code=204)
async def remove_favorite_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.product_id == product_id
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(fav)
    await db.commit()


@router.get("/supermarkets", response_model=PaginatedResponse)
async def list_favorite_supermarkets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(UserFavoriteSupermarket).where(UserFavoriteSupermarket.user_id == current_user.id)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    favorites = result.scalars().all()

    return {
        "items": [UserFavoriteSupermarketResponse.model_validate(f) for f in favorites],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/supermarkets", response_model=UserFavoriteSupermarketResponse, status_code=201)
async def add_favorite_supermarket(
    fav_in: UserFavoriteSupermarketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if supermarket exists
    result = await db.execute(select(Supermarket).where(Supermarket.id == fav_in.supermarket_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Supermarket not found")

    # Check duplicate
    result = await db.execute(
        select(UserFavoriteSupermarket).where(
            UserFavoriteSupermarket.user_id == current_user.id,
            UserFavoriteSupermarket.supermarket_id == fav_in.supermarket_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in favorites")

    fav = UserFavoriteSupermarket(user_id=current_user.id, supermarket_id=fav_in.supermarket_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.delete("/supermarkets/{supermarket_id}", status_code=204)
async def remove_favorite_supermarket(
    supermarket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(UserFavoriteSupermarket).where(
            UserFavoriteSupermarket.user_id == current_user.id,
            UserFavoriteSupermarket.supermarket_id == supermarket_id
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(fav)
    await db.commit()