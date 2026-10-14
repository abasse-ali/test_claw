"""
Seed script for Price Comparator database.
This script creates initial test data for demonstration purposes.
"""
import asyncio
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.supermarket import Supermarket
from app.models.category import Category
from app.models.product import Product
from app.models.price import Price
from app.models.user import User, UserRole
from app.core.security import get_password_hash

settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_supermarkets():
    """Create initial supermarkets."""
    supermarkets = [
        {
            "name": "Carrefour Market",
            "brand": "Carrefour",
            "address": "123 Rue de la Paix, Paris",
            "city": "Paris",
            "postal_code": "75001",
            "country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "phone": "01 23 45 67 89",
            "website": "https://www.carrefour.com",
            "is_active": True,
        },
        {
            "name": "Leclerc Hypercentre",
            "brand": "Leclerc",
            "address": "456 Avenue des Champs, Lyon",
            "city": "Lyon",
            "postal_code": "69001",
            "country": "FR",
            "latitude": 45.7640,
            "longitude": 4.8357,
            "phone": "04 78 90 12 34",
            "website": "https://www.leclerc.com",
            "is_active": True,
        },
        {
            "name": "Auchan Supermarche",
            "brand": "Auchan",
            "address": "789 Boulevard Central, Marseille",
            "city": "Marseille",
            "postal_code": "13001",
            "country": "FR",
            "latitude": 43.2965,
            "longitude": 5.3698,
            "phone": "04 91 23 45 67",
            "website": "https://www.auchan.fr",
            "is_active": True,
        },
    ]

    for sm_data in supermarkets:
        result = await AsyncSessionLocal().execute(
            select(Supermarket).where(Supermarket.name == sm_data["name"])
        )
        if not result.scalar_one_or_none():
            sm = Supermarket(**sm_data)
            await AsyncSessionLocal().add(sm)
            await AsyncSessionLocal().commit()
            print(f"Created supermarket: {sm.name}")
    
    await engine.dispose()


async def seed_categories():
    """Create initial categories."""
    categories = [
        {
            "name": "Lait et produits laitiers",
            "slug": "lait-produits-laitiers",
            "description": "Produits laitiers et dérivés",
            "icon": "🥛",
            "sort_order": 1,
            "is_active": True,
        },
        {
            "name": "Boulangerie et pâtisserie",
            "slug": "boulangerie-patisserie",
            "description": "Pain, viennoiseries et pâtisseries",
            "icon": "🍞",
            "sort_order": 2,
            "is_active": True,
        },
        {
            "name": "Café et thé",
            "slug": "cafe-the",
            "description": "Cafés moulus, thés et boissons",
            "icon": "☕",
            "sort_order": 3,
            "is_active": True,
        },
        {
            "name": "Yaourts et fromages",
            "slug": "yaourts-fromages",
            "description": "Yaourts, fromages frais et affinés",
            "icon": "🧀",
            "sort_order": 4,
            "is_active": True,
        },
        {
            "name": "Epicerie sucrée",
            "slug": "epicerie-sucrée",
            "description": "Sucre, café, thé et produits sucrés",
            "icon": "🍬",
            "sort_order": 5,
            "is_active": True,
        },
        {
            "name": "Boissons non alcoolisées",
            "slug": "boissons-non-alcoolisées",
            "description": "Sodas, eaux, jus de fruits",
            "icon": "🥤",
            "sort_order": 6,
            "is_active": True,
        },
    ]

    for cat_data in categories:
        result = await AsyncSessionLocal().execute(
            select(Category).where(Category.name == cat_data["name"])
        )
        if not result.scalar_one_or_none():
            cat = Category(**cat_data)
            await AsyncSessionLocal().add(cat)
            await AsyncSessionLocal().commit()
            print(f"Created category: {cat.name}")
    
    await engine.dispose()


async def seed_products():
    """Create initial products."""
    products = [
        {
            "name": "Lait UHT 1L",
            "slug": "lait-uht-1l",
            "description": "Lait entier UHT 1 litre",
            "brand": "Carrefour",
            "barcode": "3017320944035",
            "image_url": "https://example.com/products/lait-uht-1l.jpg",
            "unit": "L",
            "unit_size": 1.0,
            "category_id": 1,
            "is_active": True,
        },
        {
            "name": "Pain de mie 8 tranches",
            "slug": "pain-mie-8-tranches",
            "description": "Pain de mie moelleux 8 tranches",
            "brand": "Panier",
            "barcode": "3017320944052",
            "image_url": "https://example.com/products/pain-mie.jpg",
            "unit": "unit",
            "unit_size": 1.0,
            "category_id": 2,
            "is_active": True,
        },
        {
            "name": "Café moulu 250g",
            "slug": "cafe-moulu-250g",
            "description": "Café moulu Kraft Natural Selections",
            "brand": "Kraft Natural Selections",
            "barcode": "3017320944044",
            "image_url": "https://example.com/products/cafe-moulu.jpg",
            "unit": "g",
            "unit_size": 250.0,
            "category_id": 3,
            "is_active": True,
        },
        {
            "name": "Yaourt nature 500g",
            "slug": "yaourt-nature-500g",
            "description": "Yaourt nature 500g Yoplait",
            "brand": "Yoplait",
            "barcode": "3017320944075",
            "image_url": "https://example.com/products/yaourt-nature.jpg",
            "unit": "g",
            "unit_size": 500.0,
            "category_id": 4,
            "is_active": True,
        },
        {
            "name": "Riz basmati 1kg",
            "slug": "riz-basmati-1kg",
            "description": "Riz basmati 1kg Basmati",
            "brand": "Basmati",
            "barcode": "3017320944045",
            "image_url": "https://example.com/products/riz-basmati.jpg",
            "unit": "kg",
            "unit_size": 1.0,
            "category_id": 5,
            "is_active": True,
        },
        {
            "name": "Coca-Cola 2L",
            "slug": "coca-cola-2l",
            "description": "Coca-Cola zéro 2 litres",
            "brand": "Coca-Cola",
            "barcode": "3017320944076",
            "image_url": "https://example.com/products/coca-cola.jpg",
            "unit": "L",
            "unit_size": 2.0,
            "category_id": 6,
            "is_active": True,
        },
    ]

    for prod_data in products:
        result = await AsyncSessionLocal().execute(
            select(Product).where(Product.barcode == prod_data["barcode"])
        )
        if not result.scalar_one_or_none():
            prod = Product(**prod_data)
            await AsyncSessionLocal().add(prod)
            await AsyncSessionLocal().commit()
            print(f"Created product: {prod.name}")
    
    await engine.dispose()


async def seed_prices():
    """Create initial prices for supermarkets."""
    # Get all supermarkets and products
    async with AsyncSessionLocal() as db:
        supermarkets = await db.execute(select(Supermarket))
        products = await db.execute(select(Product))
        supermarket_list = supermarkets.scalars().all()
        product_list = products.scalars().all()

        for sm in supermarket_list:
            for prod in product_list:
                # Create price with random variation
                base_price = float(prod.unit_size) * 10  # Mock base price
                price_variation = base_price * (0.8 + 0.4 * random.random())
                is_promotion = random.choice([True, False])
                
                price = Price(
                    product_id=prod.id,
                    supermarket_id=sm.id,
                    price=round(price_variation, 2),
                    original_price=round(price_variation * 1.25, 2) if is_promotion else None,
                    is_promotion=is_promotion,
                    promotion_label="-20%" if is_promotion else None,
                    promotion_end_date=datetime.now(UTC) + timedelta(days=random.randint(1, 30)) if is_promotion else None,
                    currency="EUR",
                    source_url=f"https://{sm.brand.lower()}.com/product/{prod.barcode}",
                    scraped_at=datetime.now(UTC),
                    is_available=random.choice([True, False]),
                )
                db.add(price)

                # Create price history
                from app.models.price_history import PriceHistory
                history = PriceHistory(
                    product_id=prod.id,
                    supermarket_id=sm.id,
                    price=price.price,
                    original_price=price.original_price,
                    is_promotion=price.is_promotion,
                    recorded_at=datetime.now(UTC),
                )
                db.add(history)
        
        await db.commit()
        print(f"Created {len(supermarket_list) * len(product_list)} price records")
    
    await engine.dispose()


async def seed_users():
    """Create initial users."""
    users = [
        {
            "email": "admin@pricecomp.com",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "user@example.com",
            "hashed_password": get_password_hash("user123"),
            "full_name": "Test User",
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": True,
            "latitude": 48.8566,
            "longitude": 2.3522,
        },
        {
            "email": "mary@example.com",
            "hashed_password": get_password_hash("mary123"),
            "full_name": "Marie Dubois",
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": True,
            "latitude": 45.7640,
            "longitude": 4.8357,
        },
    ]

    for user_data in users:
        result = await AsyncSessionLocal().execute(
            select(User).where(User.email == user_data["email"])
        )
        if not result.scalar_one_or_none():
            user = User(**user_data)
            await AsyncSessionLocal().add(user)
            await AsyncSessionLocal().commit()
            print(f"Created user: {user.email}")
    
    await engine.dispose()


async def main():
    """Run all seeding functions."""
    import random
    from datetime import timedelta
    
    print("Seeding supermarkets...")
    await seed_supermarkets()
    
    print("Seeding categories...")
    await seed_categories()
    
    print("Seeding products...")
    await seed_products()
    
    print("Seeding prices...")
    await seed_prices()
    
    print("Seeding users...")
    await seed_users()
    
    print("Seeding complete!")


if __name__ == "__main__":
    import random
    from datetime import timedelta
    
    asyncio.run(main())