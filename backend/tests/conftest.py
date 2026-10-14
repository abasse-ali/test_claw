import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from app.main import app
from app.core.database import Base, engine, AsyncSessionLocal
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.supermarket import Supermarket
from app.models.category import Category
from app.models.product import Product
from app.models.price import Price
from app.models.price_history import PriceHistory

settings = get_settings()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
def db_session():
    """Create a fresh database session for tests."""
    async def _get_session():
        async with AsyncSessionLocal() as session:
            yield session
    return _get_session


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_test_db(monkeypatch):
    """Set up test database before each test."""
    from app.main import app
    app.dependency_overrides[engine] = engine
    
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up tables after each test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)