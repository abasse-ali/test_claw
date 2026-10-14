from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from datetime import datetime, UTC
from decimal import Decimal

from app.models.supermarket import Supermarket
from app.models.category import Category
from app.models.product import Product
from app.models.price import Price
from app.models.price_alert import PriceAlert
from app.models.user_favorite import UserFavorite
from app.models.user_favorite_supermarket import UserFavoriteSupermarket


class SupermarketService:
    async def get_nearby_supermarkets(
        self,
        lat: float,
        lon: float,
        radius_km: float = 10.0,
        db: AsyncSession = None,
    ) -> List[Supermarket]:
        """Get supermarkets near a location within radius."""
        result = await db.execute(select(Supermarket).where(Supermarket.is_active == True))
        supermarkets = result.scalars().all()

        nearby = []
        for sm in supermarkets:
            if sm.latitude and sm.longitude:
                dist = self._haversine_distance(lat, lon, sm.latitude, sm.longitude)
                if dist <= radius_km:
                    sm.distance_km = round(dist, 2)
                    nearby.append(sm)

        nearby.sort(key=lambda x: x.distance_km or 999)
        return nearby

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points using Haversine formula."""
        from math import radians, sin, cos, acos
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return R * 2 * acos(min(1, max(-1, a)))

    async def search_products(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        brand: Optional[str] = None,
        barcode: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        supermarket_id: Optional[int] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 10.0,
        is_promotion: Optional[bool] = None,
        in_stock_only: bool = True,
        sort_by: str = "price_asc",
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = None,
    ) -> tuple[List[Product], int]:
        """Search products with filters and pagination."""
        # Build base query
        stmt = select(Product).where(Product.is_active == True)

        # Add filters
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if brand:
            stmt = stmt.where(Product.brand.ilike(f"%{brand}%"))
        if barcode:
            stmt = stmt.where(Product.barcode == barcode)
        if query:
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                )
            )

        # Price filtering
        if min_price is not None or max_price is not None:
            # Get product IDs with prices in range
            price_stmt = select(Price.product_id)
            if min_price is not None:
                price_stmt = price_stmt.where(Price.price >= min_price)
            if max_price is not None:
                price_stmt = price_stmt.where(Price.price <= max_price)
            
            price_result = await db.execute(price_stmt)
            valid_product_ids = [row[0] for row in price_result]
            stmt = stmt.where(Product.id.in_(valid_product_ids))

        # Location filtering
        if latitude and longitude:
            if radius_km > 0:
                # Get nearby supermarkets
                nearby_sm_result = await db.execute(
                    select(Supermarket.id).where(
                        Supermarket.is_active == True,
                        Supermarket.latitude.isnot(None),
                        Supermarket.longitude.isnot(None)
                    )
                )
                nearby_sm_ids = [row[0] for row in nearby_sm_result]

                # Filter products that have prices at nearby supermarkets
                if nearby_sm_ids:
                    product_stmt = select(Price.product_id.distinct())
                    product_stmt = product_stmt.where(Price.supermarket_id.in_(nearby_sm_ids))
                    nearby_product_result = await db.execute(product_stmt)
                    nearby_product_ids = [row[0] for row in nearby_product_result]
                    stmt = stmt.where(Product.id.in_(nearby_product_ids))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # Apply sorting and pagination
        if sort_by == "price_asc":
            stmt = stmt.order_by(Product.name)
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Product.name.desc())
        elif sort_by == "newest":
            stmt = stmt.order_by(Product.created_at.desc())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        products = result.scalars().all()

        return list(products), total

    async def get_category_tree(self, db: AsyncSession = None) -> List[Category]:
        """Get hierarchical category tree."""
        result = await db.execute(select(Category).where(Category.is_active == True).order_by(Category.sort_order))
        categories = result.scalars().all()

        # Build tree
        cat_dict = {c.id: c for c in categories}
        roots = []
        for c in categories:
            if c.parent_id and c.parent_id in cat_dict:
                cat_dict[c.parent_id].children.append(cat_dict[c.id])
            else:
                roots.append(cat_dict[c.id])
        return roots

    async def update_user_location(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        db: AsyncSession = None,
    ) -> Optional[User]:
        """Update user location."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.latitude = latitude
            user.longitude = longitude
            await db.commit()
            await db.refresh(user)
        return user


class ProductService:
    async def get_product_with_comparison(
        self,
        product_id: int,
        db: AsyncSession = None,
    ) -> Optional[Product]:
        """Get product with price comparison."""
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        return product

    async def create_product(
        self,
        product_data: dict,
        db: AsyncSession = None,
    ) -> Product:
        """Create new product."""
        # Generate slug if not provided
        if "slug" not in product_data:
            product_data["slug"] = product_data["name"].lower().replace(" ", "-")

        product = Product(**product_data)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    async def update_product(
        self,
        product_id: int,
        update_data: dict,
        db: AsyncSession = None,
    ) -> Optional[Product]:
        """Update product."""
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            for field, value in update_data.items():
                setattr(product, field, value)
            await db.commit()
            await db.refresh(product)
        return product