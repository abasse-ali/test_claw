from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, 
    Text, Boolean, Enum as SQLEnum, UniqueConstraint, DECIMAL
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    preferred_radius_km = Column(Float, default=10.0, nullable=False)
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