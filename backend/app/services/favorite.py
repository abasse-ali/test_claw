from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.user_favorite import UserFavorite
from app.models.user_favorite_supermarket import UserFavoriteSupermarket
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User


class FavoriteService:
    async def add_product_favorite(
        self,
        user_id: int,
        product_id: int,
        db: AsyncSession = None,
    ) -> UserFavorite:
        """Add product to user's favorites."""
        # Check if product exists
        product_result = await db.execute(select(Product).where(Product.id == product_id))
        if not product_result.scalar_one_or_none():
            raise ValueError("Product not found")

        # Check duplicate
        existing_result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.product_id == product_id
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError("Product already in favorites")

        favorite = UserFavorite(user_id=user_id, product_id=product_id)
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite

    async def remove_product_favorite(
        self,
        user_id: int,
        product_id: int,
        db: AsyncSession = None,
    ) -> bool:
        """Remove product from user's favorites."""
        result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.product_id == product_id
            )
        )
        favorite = result.scalar_one_or_none()
        if favorite:
            await db.delete(favorite)
            await db.commit()
            return True
        return False

    async def get_user_product_favorites(
        self,
        user_id: int,
        db: AsyncSession = None,
    ) -> List[UserFavorite]:
        """Get all product favorites for a user."""
        result = await db.execute(
            select(UserFavorite).where(UserFavorite.user_id == user_id)
        )
        return result.scalars().all()

    async def add_supermarket_favorite(
        self,
        user_id: int,
        supermarket_id: int,
        db: AsyncSession = None,
    ) -> UserFavoriteSupermarket:
        """Add supermarket to user's favorites."""
        # Check if supermarket exists
        sm_result = await db.execute(select(Supermarket).where(Supermarket.id == supermarket_id))
        if not sm_result.scalar_one_or_none():
            raise ValueError("Supermarket not found")

        # Check duplicate
        existing_result = await db.execute(
            select(UserFavoriteSupermarket).where(
                UserFavoriteSupermarket.user_id == user_id,
                UserFavoriteSupermarket.supermarket_id == supermarket_id
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError("Supermarket already in favorites")

        favorite = UserFavoriteSupermarket(user_id=user_id, supermarket_id=supermarket_id)
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite

    async def remove_supermarket_favorite(
        self,
        user_id: int,
        supermarket_id: int,
        db: AsyncSession = None,
    ) -> bool:
        """Remove supermarket from user's favorites."""
        result = await db.execute(
            select(UserFavoriteSupermarket).where(
                UserFavoriteSupermarket.user_id == user_id,
                UserFavoriteSupermarket.supermarket_id == supermarket_id
            )
        )
        favorite = result.scalar_one_or_none()
        if favorite:
            await db.delete(favorite)
            await db.commit()
            return True
        return False

    async def get_user_supermarket_favorites(
        self,
        user_id: int,
        db: AsyncSession = None,
    ) -> List[UserFavoriteSupermarket]:
        """Get all supermarket favorites for a user."""
        result = await db.execute(
            select(UserFavoriteSupermarket).where(UserFavoriteSupermarket.user_id == user_id)
        )
        return result.scalars().all()