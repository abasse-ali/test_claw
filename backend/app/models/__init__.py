from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, 
    Text, Boolean, Enum as SQLEnum, UniqueConstraint, DECIMAL
)
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    latitude = Column(Float, nullable=True)  # For nearby supermarkets
    longitude = Column(Float, nullable=True)
    preferred_radius_km = Column(Float, default=10.0, nullable=False)  # Search radius
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    alerts = relationship("PriceAlert", back_populates="user", lazy="dynamic")
    favorite_products = relationship("UserFavorite", back_populates="user", lazy="dynamic")
    favorite_supermarkets = relationship("UserFavoriteSupermarket", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email}>"


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorite_products")
    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_favorite_product"),
    )


class UserFavoriteSupermarket(Base):
    __tablename__ = "user_favorite_supermarkets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorite_supermarkets")
    supermarket = relationship("Supermarket")

    __table_args__ = (
        UniqueConstraint("user_id", "supermarket_id", name="uq_user_favorite_supermarket"),
    )


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