from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, UTC, timedelta
from decimal import Decimal

from app.models.price_history import PriceHistory
from app.models.price_alert import PriceAlert
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User


class PriceHistoryService:
    async def get_price_history(
        self,
        product_id: int,
        supermarket_id: Optional[int] = None,
        days: int = 30,
        db: AsyncSession = None,
    ) -> List[PriceHistory]:
        """Get price history for a product."""
        stmt = select(PriceHistory).where(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= datetime.now(UTC) - timedelta(days=days)
        )
        
        if supermarket_id:
            stmt = stmt.where(PriceHistory.supermarket_id == supermarket_id)
        
        stmt = stmt.order_by(PriceHistory.recorded_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_price_history(
        self,
        product_id: int,
        supermarket_id: int,
        price_data: dict,
        db: AsyncSession = None,
    ) -> PriceHistory:
        """Create price history record."""
        history = PriceHistory(
            product_id=product_id,
            supermarket_id=supermarket_id,
            price=price_data.get("price"),
            original_price=price_data.get("original_price"),
            is_promotion=price_data.get("is_promotion", False),
            recorded_at=datetime.now(UTC),
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


class AlertService:
    async def create_alert(
        self,
        user_id: int,
        alert_data: dict,
        db: AsyncSession = None,
    ) -> PriceAlert:
        """Create new price alert."""
        # Check if product exists and is active
        product_result = await db.execute(select(Product).where(Product.id == alert_data["product_id"]))
        if not product_result.scalar_one_or_none():
            raise ValueError("Product not found")

        # Check duplicate alert
        existing_result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.user_id == user_id,
                PriceAlert.product_id == alert_data["product_id"],
                PriceAlert.supermarket_id == alert_data.get("supermarket_id"),
                PriceAlert.is_active == True
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError("Alert for this product/supermarket already exists")

        # Check max alerts per user
        alert_count_result = await db.execute(
            select(func.count()).select_from(PriceAlert).where(
                PriceAlert.user_id == user_id,
                PriceAlert.is_active == True
            )
        )
        alert_count = alert_count_result.scalar()
        if alert_count >= 50:  # Max alerts per user
            raise ValueError("Maximum alerts per user reached")

        alert = PriceAlert(user_id=user_id, **alert_data)
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def check_alerts(self, db: AsyncSession = None) -> List[PriceAlert]:
        """Check all active alerts for price drops."""
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)
        )
        alerts = result.scalars().all()

        triggered_alerts = []
        for alert in alerts:
            # Get current price for this product at this supermarket
            price_result = await db.execute(
                select(Price).where(
                    Price.product_id == alert.product_id,
                    Price.supermarket_id == alert.supermarket_id if alert.supermarket_id else Price.supermarket_id,
                    Price.is_available == True
                ).order_by(Price.scraped_at.desc()).limit(1)
            )
            current_price = price_result.scalar_one_or_none()

            if current_price and current_price.price <= alert.target_price:
                # Trigger alert
                alert.current_price = current_price.price
                alert.last_triggered_at = datetime.now(UTC)
                triggered_alerts.append(alert)

        await db.commit()
        return triggered_alerts

    async def get_user_alerts(
        self,
        user_id: int,
        db: AsyncSession = None,
    ) -> List[PriceAlert]:
        """Get all alerts for a user."""
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.user_id == user_id)
        )
        return result.scalars().all()

    async def update_alert(
        self,
        alert_id: int,
        user_id: int,
        update_data: dict,
        db: AsyncSession = None,
    ) -> Optional[PriceAlert]:
        """Update alert."""
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == user_id
            )
        )
        alert = result.scalar_one_or_none()
        if alert:
            for field, value in update_data.items():
                setattr(alert, field, value)
            await db.commit()
            await db.refresh(alert)
        return alert

    async def delete_alert(
        self,
        alert_id: int,
        user_id: int,
        db: AsyncSession = None,
    ) -> bool:
        """Delete alert."""
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == user_id
            )
        )
        alert = result.scalar_one_or_none()
        if alert:
            await db.delete(alert)
            await db.commit()
            return True
        return False