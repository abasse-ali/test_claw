from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/price_comparator", alias="DATABASE_URL")
    database_url_sync: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/price_comparator", alias="DATABASE_URL_SYNC")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", alias="CELERY_RESULT_BACKEND")

    # Security
    secret_key: str = Field(default="your-super-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Scraping
    scraping_delay_min: int = Field(default=2, alias="SCRAPING_DELAY_MIN")
    scraping_delay_max: int = Field(default=5, alias="SCRAPING_DELAY_MAX")
    scraping_timeout: int = Field(default=30, alias="SCRAPING_TIMEOUT")
    respect_robots_txt: bool = Field(default=True, alias="RESPECT_ROBOTS_TXT")
    user_agent: str = Field(default="PriceComparator/1.0", alias="USER_AGENT")

    # Alerts
    alert_check_interval_minutes: int = Field(default=60, alias="ALERT_CHECK_INTERVAL_MINUTES")
    max_alerts_per_user: int = Field(default=50, alias="MAX_ALERTS_PER_USER")

    # External APIs
    openstreetmap_api: str = Field(default="https://nominatim.openstreetmap.org", alias="OPENSTREETMAP_API")
    geocoding_api_key: Optional[str] = Field(default=None, alias="GEOCODING_API_KEY")

    # App
    app_name: str = Field(default="Price Comparator", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()