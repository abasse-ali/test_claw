from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from decimal import Decimal

from app.models.price import Price
from app.models.product import Product
from app.models.supermarket import Supermarket


class PriceService:
    async def get_price_comparison(
        self,
        product_id: int,
        db: AsyncSession = None,
    ) -> Optional[dict]:
        """Get price comparison for a product."""
        # Get product
        product_result = await db.execute(select(Product).where(Product.id == product_id))
        product = product_result.scalar_one_or_none()
        if not product:
            return None

        # Get all prices for this product
        prices_result = await db.execute(
            select(Price).where(Price.product_id == product_id)
            .order_by(Price.price)
        )
        prices = prices_result.scalars().all()

        if not prices:
            return {
                "product": product,
                "prices": [],
                "cheapest": None,
                "most_expensive": None,
                "average_price": Decimal("0"),
                "price_spread": Decimal("0"),
            }

        # Find cheapest and most expensive
        cheapest = prices[0]
        most_expensive = prices[-1]

        # Calculate average and spread
        total_price = sum(float(p.price) for p in prices)
        avg_price = Decimal(str(total_price / len(prices)))
        spread = most_expensive.price - cheapest.price

        return {
            "product": product,
            "prices": prices,
            "cheapest": cheapest,
            "most_expensive": most_expensive,
            "average_price": avg_price,
            "price_spread": spread,
        }

    async def create_price(
        self,
        price_data: dict,
        db: AsyncSession = None,
    ) -> Price:
        """Create new price record."""
        # Check if product exists
        product_result = await db.execute(select(Product).where(Product.id == price_data["product_id"]))
        if not product_result.scalar_one_or_none():
            raise ValueError("Product not found")

        # Check if supermarket exists
        sm_result = await db.execute(select(Supermarket).where(Supermarket.id == price_data["supermarket_id"]))
        if not sm_result.scalar_one_or_none():
            raise ValueError("Supermarket not found")

        # Check for duplicate price at same time for same product+supermarket
        existing_result = await db.execute(
            select(Price).where(
                Price.product_id == price_data["product_id"],
                Price.supermarket_id == price_data["supermarket_id"],
                Price.scraped_at == price_data.get("scraped_at")
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError("Price already exists for this product/supermarket at this time")

        # Create price
        price = Price(**price_data)
        db.add(price)
        
        # Create price history
        from app.models.price_history import PriceHistory
        history = PriceHistory(
            product_id=price_data["product_id"],
            supermarket_id=price_data["supermarket_id"],
            price=price_data["price"],
            original_price=price_data.get("original_price"),
            is_promotion=price_data.get("is_promotion", False),
            recorded_at=price_data.get("recorded_at", price_data.get("scraped_at")),
        )
        db.add(history)

        await db.commit()
        await db.refresh(price)
        return price

    async def get_price_stats(
        self,
        product_id: int,
        db: AsyncSession = None,
    ) -> dict:
        """Get price statistics for a product."""
        result = await db.execute(
            select(
                func.min(Price.price).label("min_price"),
                func.max(Price.price).label("max_price"),
                func.avg(Price.price).label("avg_price"),
                func.count(Price.id).label("price_count"),
            ).where(Price.product_id == product_id)
        )
        
        stats = result.first()
        if not stats:
            return {
                "min_price": Decimal("0"),
                "max_price": Decimal("0"),
                "avg_price": Decimal("0"),
                "cheapest_supermarket": None,
                "price_count": 0,
            }

        # Get cheapest supermarket
        cheapest_result = await db.execute(
            select(Price).where(Price.product_id == product_id)
            .order_by(Price.price).limit(1)
        )
        cheapest_price = cheapest_result.scalar_one_or_none()
        cheapest_sm = None
        if cheapest_price:
            sm_result = await db.execute(
                select(Supermarket).where(Supermarket.id == cheapest_price.supermarket_id)
            )
            cheapest_sm = sm_result.scalar_one_or_none()

        return {
            "min_price": stats.min_price or Decimal("0"),
            "max_price": stats.max_price or Decimal("0"),
            "avg_price": Decimal(str(stats.avg_price)) if stats.avg_price else Decimal("0"),
            "cheapest_supermarket": cheapest_sm,
            "price_count": stats.price_count or 0,
        }