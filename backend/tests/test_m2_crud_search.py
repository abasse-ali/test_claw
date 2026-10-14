import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.supermarket import Supermarket
from app.models.category import Category
from app.models.product import Product
from app.models.price import Price
from app.models.price_alert import PriceAlert
from app.models.user import User, UserRole
from app.core.security import get_password_hash


settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_supermarket_crud():
    """Test supermarket CRUD operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a user and login
        user_data = {
            "email": "testadmin@example.com",
            "full_name": "Test Admin",
            "password": "admin123",
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a supermarket
        supermarket_data = {
            "name": "Test Supermarket",
            "brand": "Test",
            "address": "123 Test Street, Test City",
            "city": "Test City",
            "postal_code": "12345",
            "country": "FR",
            "phone": "01 23 45 67 89",
            "website": "https://test.com",
        }
        
        response = await client.post("/supermarkets", json=supermarket_data, headers=headers)
        assert response.status_code == 201
        supermarket = response.json()
        assert supermarket["name"] == supermarket_data["name"]
        assert supermarket["brand"] == supermarket_data["brand"]
        assert supermarket["id"] > 0
        
        # Get the created supermarket
        response = await client.get(f"/supermarkets/{supermarket['id']}", headers=headers)
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == supermarket["id"]
        assert retrieved["name"] == supermarket_data["name"]
        
        # Update the supermarket
        update_data = {
            "name": "Updated Test Supermarket",
            "city": "Updated City",
        }
        
        response = await client.patch(f"/supermarkets/{supermarket['id']}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["city"] == update_data["city"]
        
        # Delete the supermarket
        response = await client.delete(f"/supermarkets/{supermarket['id']}", headers=headers)
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/supermarkets/{supermarket['id']}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_category_crud():
    """Test category CRUD operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create user and login
        user_data = {
            "email": "testcat@example.com",
            "full_name": "Test Category User",
            "password": "cat123",
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a category
        category_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "Test category description",
            "sort_order": 99,
        }
        
        response = await client.post("/categories", json=category_data, headers=headers)
        assert response.status_code == 201
        category = response.json()
        assert category["name"] == category_data["name"]
        assert category["slug"] == category_data["slug"]
        assert category["id"] > 0
        
        # Get the created category
        response = await client.get(f"/categories/{category['id']}", headers=headers)
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == category["id"]
        assert retrieved["name"] == category_data["name"]
        
        # Update the category
        update_data = {
            "name": "Updated Test Category",
            "sort_order": 1,
        }
        
        response = await client.patch(f"/categories/{category['id']}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["sort_order"] == update_data["sort_order"]
        
        # Delete the category
        response = await client.delete(f"/categories/{category['id']}", headers=headers)
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/categories/{category['id']}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_product_crud():
    """Test product CRUD operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create user and login
        user_data = {
            "email": "testprod@example.com",
            "full_name": "Test Product User",
            "password": "prod123",
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a product
        product_data = {
            "name": "Test Product",
            "slug": "test-product",
            "description": "Test product description",
            "brand": "Test Brand",
            "barcode": "1234567890123",
            "unit": "unit",
            "unit_size": 1.0,
            "category_id": 1,  # Assuming category 1 exists from seeding
            "is_active": True,
        }
        
        response = await client.post("/products", json=product_data, headers=headers)
        assert response.status_code == 201
        product = response.json()
        assert product["name"] == product_data["name"]
        assert product["slug"] == product_data["slug"]
        assert product["id"] > 0
        
        # Get the created product
        response = await client.get(f"/products/{product['id']}", headers=headers)
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == product["id"]
        assert retrieved["name"] == product_data["name"]
        
        # Update the product
        update_data = {
            "name": "Updated Test Product",
            "description": "Updated description",
            "is_active": False,
        }
        
        response = await client.patch(f"/products/{product['id']}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["description"] == update_data["description"]
        assert updated["is_active"] == update_data["is_active"]
        
        # Delete the product
        response = await client.delete(f"/products/{product['id']}", headers=headers)
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/products/{product['id']}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_product_search_filters():
    """Test product search with various filters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with query parameter
        response = await client.get("/products/search", params={"q": "lait"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        # Test with category filter
        response = await client.get("/products/search", params={"category_id": 1})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # Test with brand filter
        response = await client.get("/products/search", params={"brand": "Carrefour"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # Test with barcode filter
        response = await client.get("/products/search", params={"barcode": "3017320944035"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Should return at most 1 item for exact barcode match


@pytest.mark.asyncio
async def test_nearby_supermarkets():
    """Test nearby supermarkets search."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Search for supermarkets near Paris (using seeded data)
        response = await client.get(
            "/supermarkets/nearby",
            params={"lat": 48.8566, "lon": 2.3522, "radius_km": 50}
        )
        assert response.status_code == 200
        supermarkets = response.json()
        
        # Should have at least some supermarkets in Paris region
        assert len(supermarkets) > 0
        
        # All returned supermarkets should be within 50km
        for sm in supermarkets:
            assert "distance_km" in sm
            assert sm["distance_km"] <= 50
        
        # Should be sorted by distance
        distances = [sm["distance_km"] for sm in supermarkets]
        assert distances == sorted(distances)


@pytest.mark.asyncio
async def test_category_tree():
    """Test category tree endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/categories/tree")
        assert response.status_code == 200
        categories = response.json()
        
        assert isinstance(categories, list)
        
        # Verify tree structure
        def verify_tree(items, depth=0):
            for item in items:
                assert "id" in item
                assert "name" in item
                assert "children" in item
                assert isinstance(item["children"], list)
                if depth < 3:  # Limit recursion
                    verify_tree(item["children"], depth + 1)
        
        verify_tree(categories)