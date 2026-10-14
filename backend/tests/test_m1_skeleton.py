import pytest
import asyncio
from httpx import AsyncClient
from app.core.config import get_settings
from app.models.user import User
from app.core.security import get_password_hash


settings = get_settings()


@pytest.mark.asyncio
async def test_health_check():
    """Test the health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == settings.app_name


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to Price Comparator API" in data["message"]
        assert "/docs" in data["docs"]


@pytest.mark.asyncio
async def test_supermarket_search():
    """Test supermarket search endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get nearby supermarkets
        response = await client.get(
            "/supermarkets/nearby",
            params={"lat": 48.8566, "lon": 2.3522, "radius_km": 10}
        )
        assert response.status_code == 200
        supermarkets = response.json()
        assert len(supermarkets) >= 3
        
        # Check that all returned supermarkets have distance
        for sm in supermarkets:
            assert "distance_km" in sm
            assert sm["distance_km"] <= 10
        
        # Check sorting (closest first)
        distances = [sm["distance_km"] for sm in supermarkets]
        assert distances == sorted(distances)


@pytest.mark.asyncio
async def test_product_search():
    """Test product search endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Search for milk
        response = await client.get(
            "/products/search",
            params={"q": "lait", "page": 1, "page_size": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        
        # Check that we got results (should be seeded data)
        assert data["total"] > 0


@pytest.mark.asyncio
async def test_user_registration_login():
    """Test user registration and login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register a new user
        user_data = {
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password": "password123",
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["full_name"] == user_data["full_name"]
        assert "password" not in user
        
        # Login with the new user
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Get user profile with token
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_auth_required_endpoints():
    """Test that protected endpoints require authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        endpoints = [
            ("/users/me", "GET"),
            ("/products", "GET"),
            ("/alerts", "GET"),
            ("/favorites/products", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={})
            
            # Should return 401 or 403 without authentication
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require auth"


@pytest.mark.asyncio
async def test_price_comparison():
    """Test price comparison endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # This should work with seeded data
        response = await client.get("/prices/product/1/comparison")
        # Might be 404 if we don't have product 1, but should not be server error
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "product" in data
            assert "prices" in data
            assert "cheapest" in data
            assert "most_expensive" in data
            assert "average_price" in data
            assert "price_spread" in data


@pytest.mark.asyncio
async def test_category_tree():
    """Test category tree endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/categories/tree")
        assert response.status_code == 200
        categories = response.json()
        
        # Should return a list
        assert isinstance(categories, list)
        
        # Check tree structure
        def check_tree(items, depth=0):
            for item in items:
                assert "id" in item
                assert "name" in item
                assert "children" in item
                if depth < 3:  # Limit recursion depth
                    check_tree(item["children"], depth + 1)
        
        check_tree(categories)