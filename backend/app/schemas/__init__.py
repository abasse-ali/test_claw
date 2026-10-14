from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_radius_km: Optional[float] = Field(default=10.0, ge=0.1, le=100)


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_radius_km: float
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Supermarket Schemas
class SupermarketBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    address: str
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=10)
    country: str = Field(default="FR", min_length=2, max_length=2)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    opening_hours: Optional[str] = None


class SupermarketCreate(SupermarketBase):
    pass


class SupermarketUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    opening_hours: Optional[str] = None
    is_active: Optional[bool] = None


class SupermarketResponse(SupermarketBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    distance_km: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SupermarketWithPrices(SupermarketResponse):
    prices_count: int = 0


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryTree(CategoryResponse):
    children: List["CategoryTree"] = []


CategoryTree.model_rebuild()


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    brand: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, min_length=8, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)
    unit: str = Field(default="unit", max_length=20)
    unit_size: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    brand: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, min_length=8, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = Field(None, max_length=20)
    unit_size: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    current_prices: List["PriceResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class ProductWithPrices(ProductResponse):
    prices: List["PriceResponse"] = []
    price_stats: Optional["ProductPriceStats"] = None


class ProductPriceStats(BaseModel):
    min_price: Decimal
    max_price: Decimal
    avg_price: Decimal
    cheapest_supermarket: Optional[SupermarketResponse] = None
    price_count: int


# Price Schemas
class PriceBase(BaseModel):
    product_id: int
    supermarket_id: int
    price: Decimal = Field(..., ge=0, decimal_places=2)
    original_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_promotion: bool = False
    promotion_label: Optional[str] = Field(None, max_length=100)
    promotion_end_date: Optional[datetime] = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    source_url: Optional[str] = Field(None, max_length=500)
    is_available: bool = True


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    original_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_promotion: Optional[bool] = None
    promotion_label: Optional[str] = Field(None, max_length=100)
    promotion_end_date: Optional[datetime] = None
    is_available: Optional[bool] = None


class PriceResponse(PriceBase):
    id: int
    scraped_at: datetime
    product: Optional[ProductResponse] = None
    supermarket: Optional[SupermarketResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PriceComparisonResponse(BaseModel):
    product: ProductResponse
    prices: List[PriceResponse]
    cheapest: Optional[PriceResponse] = None
    most_expensive: Optional[PriceResponse] = None
    average_price: Decimal
    price_spread: Decimal  # max - min


# Price History Schemas
class PriceHistoryPoint(BaseModel):
    date: datetime
    price: Decimal
    original_price: Optional[Decimal] = None
    is_promotion: bool
    supermarket_id: int
    supermarket_name: str


class PriceHistoryResponse(BaseModel):
    product_id: int
    product_name: str
    history: List[PriceHistoryPoint]
    period_days: int


# Price Alert Schemas
class PriceAlertBase(BaseModel):
    product_id: int
    supermarket_id: Optional[int] = None
    target_price: Decimal = Field(..., gt=0, decimal_places=2)
    notify_email: bool = True
    notify_push: bool = False


class PriceAlertCreate(PriceAlertBase):
    pass


class PriceAlertUpdate(BaseModel):
    target_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    supermarket_id: Optional[int] = None
    notify_email: Optional[bool] = None
    notify_push: Optional[bool] = None
    is_active: Optional[bool] = None


class PriceAlertResponse(PriceAlertBase):
    id: int
    user_id: int
    current_price: Optional[Decimal] = None
    is_active: bool
    last_triggered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None
    supermarket: Optional[SupermarketResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Favorite Schemas
class UserFavoriteCreate(BaseModel):
    product_id: int


class UserFavoriteResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class UserFavoriteSupermarketCreate(BaseModel):
    supermarket_id: int


class UserFavoriteSupermarketResponse(BaseModel):
    id: int
    user_id: int
    supermarket_id: int
    created_at: datetime
    supermarket: SupermarketResponse

    model_config = ConfigDict(from_attributes=True)


# Search Schemas
class ProductSearchParams(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    supermarket_id: Optional[int] = None
    city: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(default=10, gt=0, le=100)
    is_promotion: Optional[bool] = None
    in_stock_only: bool = True
    sort_by: Literal["price_asc", "price_desc", "relevance", "newest"] = "price_asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Scraping Schemas
class ScrapingJobCreate(BaseModel):
    supermarket_id: int


class ScrapingJobResponse(BaseModel):
    id: int
    supermarket_id: int
    supermarket_name: str
    status: str
    products_scraped: int
    products_updated: int
    products_new: int
    errors: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Stats Schemas
class DashboardStats(BaseModel):
    total_products: int
    total_supermarkets: int
    total_prices: int
    total_alerts: int
    active_alerts: int
    recent_scraping_jobs: List[ScrapingJobResponse]


# Error Schemas
class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorResponse(BaseModel):
    detail: List[dict]