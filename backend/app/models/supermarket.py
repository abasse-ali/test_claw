from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, 
    Text, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Supermarket(Base):
    __tablename__ = "supermarkets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=True)  # e.g., "Carrefour", "Leclerc"
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(2), default="FR", nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    opening_hours = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    prices = relationship("Price", back_populates="supermarket", lazy="dynamic")

    __table_args__ = (
        Index("ix_supermarkets_location", "latitude", "longitude"),
        Index("ix_supermarkets_city_brand", "city", "brand"),
    )

    def __repr__(self):
        return f"<Supermarket {self.name} ({self.city})>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    # Self-referential relationship
    parent = relationship("Category", remote_side=[id], backref="children")

    # Relationships
    products = relationship("Product", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    brand = Column(String(100), nullable=True, index=True)
    barcode = Column(String(20), nullable=True, unique=True, index=True)  # EAN13
    image_url = Column(String(500), nullable=True)
    unit = Column(String(20), nullable=False, default="unit")  # kg, L, unit, pack
    unit_size = Column(Float, nullable=True)  # e.g., 1.5 for 1.5L
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    prices = relationship("Price", back_populates="product", lazy="dynamic")
    alerts = relationship("PriceAlert", back_populates="product", lazy="dynamic")

    __table_args__ = (
        Index("ix_products_brand_category", "brand", "category_id"),
        Index("ix_products_name_brand", "name", "brand"),
    )

    def __repr__(self):
        return f"<Product {self.name} ({self.brand})>"