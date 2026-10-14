from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, supermarkets, products, prices, alerts, scraping, categories, favorites, price_history

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(supermarkets.router, prefix="/supermarkets", tags=["supermarkets"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(scraping.router, prefix="/scraping", tags=["scraping"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(price_history.router, prefix="/price-history", tags=["price-history"])