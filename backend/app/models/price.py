from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, 
    Text, Boolean, UniqueConstraint, DECIMAL
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)  # Price in euros with 2 decimals
    original_price = Column(DECIMAL(10, 2), nullable=True)  # Price before promotion
    is_promotion = Column(Boolean, default=False, nullable=False)
    promotion_label = Column(String(100), nullable=True)  # e.g., "-20%", "2 pour 1"
    promotion_end_date = Column(DateTime, nullable=True)
    currency = Column(String(3), default="EUR", nullable=False)
    source_url = Column(String(500), nullable=True)  # URL where price was found
    scraped_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    is_available = Column(Boolean, default=True, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="prices")
    supermarket = relationship("Supermarket", back_populates="prices")

    __table_args__ = (
        Index("ix_prices_product_supermarket_date", "product_id", "supermarket_id", "scraped_at"),
        Index("ix_prices_product_date", "product_id", "scraped_at"),
        UniqueConstraint("product_id", "supermarket_id", "scraped_at", name="uq_price_product_supermarket_date"),
    )

    def __repr__(self):
        return f"<Price {self.price}€ for Product {self.product_id} at Supermarket {self.supermarket_id}>"