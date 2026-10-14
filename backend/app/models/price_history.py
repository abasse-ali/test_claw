from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, 
    Text, Boolean, UniqueConstraint, DECIMAL
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    original_price = Column(DECIMAL(10, 2), nullable=True)
    is_promotion = Column(Boolean, default=False, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)

    # Relationships
    product = relationship("Product")
    supermarket = relationship("Supermarket")

    __table_args__ = (
        Index("ix_price_history_product_supermarket_date", "product_id", "supermarket_id", "recorded_at"),
    )

    def __repr__(self):
        return f"<PriceHistory {self.price}€ for Product {self.product_id} at {self.recorded_at}>"


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=True, index=True)  # None = any supermarket
    target_price = Column(DECIMAL(10, 2), nullable=False)  # Alert when price <= target
    current_price = Column(DECIMAL(10, 2), nullable=True)  # Last known price
    is_active = Column(Boolean, default=True, nullable=False)
    notify_email = Column(Boolean, default=True, nullable=False)
    notify_push = Column(Boolean, default=False, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")
    supermarket = relationship("Supermarket")

    def __repr__(self):
        return f"<PriceAlert user={self.user_id} product={self.product_id} target={self.target_price}>"


class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed
    products_scraped = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
    products_new = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    supermarket = relationship("Supermarket")

    def __repr__(self):
        return f"<ScrapingJob {self.id} - {self.status}>"