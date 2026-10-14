import asyncio
import random
import httpx
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from robotparser import RobotFileParser

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.scraping_job import ScrapingJob
from app.models.supermarket import Supermarket
from app.models.product import Product
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.core.config import get_settings

settings = get_settings()


class ScrapingService:
    def __init__(self):
        self.scrapers = {}
    
    def register_scraper(self, supermarket_id: int, scraper_class):
        self.scrapers[supermarket_id] = scraper_class

    async def check_robots_txt(self, url: str, user_agent: str = "PriceComparator/1.0") -> bool:
        """Check if scraping is allowed by robots.txt."""
        if not settings.respect_robots_txt:
            return True
        
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    rp = RobotFileParser()
                    rp.parse(response.text.splitlines())
                    return rp.can_fetch(user_agent, url)
        except Exception:
            pass
        
        return True  # Allow if robots.txt not found or error

    async def run_scraping_job(self, job_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Run a scraping job."""
        # Get job
        result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return {"error": "Job not found"}
        
        # Get supermarket
        sm_result = await db.execute(select(Supermarket).where(Supermarket.id == job.supermarket_id))
        supermarket = sm_result.scalar_one_or_none()
        
        if not supermarket:
            job.status = "failed"
            job.errors = "Supermarket not found"
            job.completed_at = datetime.now(UTC)
            await db.commit()
            return {"error": "Supermarket not found"}
        
        # Check if another job is running for this supermarket
        running_result = await db.execute(
            select(ScrapingJob).where(
                ScrapingJob.supermarket_id == job.supermarket_id,
                ScrapingJob.status == "running"
            )
        )
        if running_result.scalar_one_or_none():
            job.status = "failed"
            job.errors = "Another scraping job is already running for this supermarket"
            job.completed_at = datetime.now(UTC)
            await db.commit()
            return {"error": "Concurrent job running"}
        
        job.status = "running"
        job.started_at = datetime.now(UTC)
        await db.commit()
        
        try:
            # Run scraper
            scraper_class = self.scrapers.get(job.supermarket_id)
            if not scraper_class:
                raise ValueError(f"No scraper configured for supermarket {job.supermarket_id}")
            
            scraper = scraper_class(supermarket)
            result = await scraper.scrape()
            
            job.products_scraped = result.get("scraped", 0)
            job.products_updated = result.get("updated", 0)
            job.products_new = result.get("new", 0)
            job.status = "completed"
            job.errors = None
        except Exception as e:
            job.status = "failed"
            job.errors = str(e)
        finally:
            job.completed_at = datetime.now(UTC)
            await db.commit()
        
        return {
            "job_id": job.id,
            "status": job.status,
            "products_scraped": job.products_scraped,
            "products_updated": job.products_updated,
            "products_new": job.products_new,
        }


class BaseScraper:
    def __init__(self, supermarket: Supermarket):
        self.supermarket = supermarket
        self.scraped_at = datetime.now(UTC)

    async def scrape(self) -> Dict[str, Any]:
        """Scrape products from the supermarket site."""
        return {"scraped": 0, "updated": 0, "new": 0}

    async def save_product(self, db: AsyncSession, product_data: Dict[str, Any]) -> Product:
        """Save or update product and create price record."""
        # Check if product exists
        barcode = product_data.get("barcode")
        if barcode:
            result = await db.execute(select(Product).where(Product.barcode == barcode))
            product = result.scalar_one_or_none()
        else:
            product = None
        
        if product:
            # Update existing product
            product.name = product_data.get("name", product.name)
            product.brand = product_data.get("brand", product.brand)
            product.image_url = product_data.get("image_url", product.image_url)
            product.unit = product_data.get("unit", product.unit)
            product.unit_size = product_data.get("unit_size", product.unit_size)
            product.category_id = product_data.get("category_id", product.category_id)
            product.is_active = True
            product.updated_at = datetime.now(UTC)
            is_new = False
        else:
            # Create new product
            product = Product(
                name=product_data["name"],
                slug=product_data.get("slug", product_data["name"].lower().replace(" ", "-")),
                description=product_data.get("description"),
                brand=product_data.get("brand"),
                barcode=product_data.get("barcode"),
                image_url=product_data.get("image_url"),
                unit=product_data.get("unit", "unit"),
                unit_size=product_data.get("unit_size"),
                category_id=product_data.get("category_id"),
                is_active=True,
            )
            db.add(product)
            await db.commit()
            await db.refresh(product)
            is_new = True
        
        # Check if price already exists for this product+supermarket at this time
        existing_price_result = await db.execute(
            select(Price).where(
                Price.product_id == product.id,
                Price.supermarket_id == self.supermarket.id,
                Price.scraped_at == self.scraped_at
            )
        )
        existing_price = existing_price_result.scalar_one_or_none()
        
        if existing_price:
            # Update existing price
            existing_price.price = product_data["price"]
            existing_price.original_price = product_data.get("original_price")
            existing_price.is_promotion = product_data.get("is_promotion", False)
            existing_price.promotion_label = product_data.get("promotion_label")
            existing_price.promotion_end_date = product_data.get("promotion_end_date")
            existing_price.currency = product_data.get("currency", "EUR")
            existing_price.source_url = product_data.get("source_url")
            existing_price.is_available = product_data.get("is_available", True)
            price = existing_price
        else:
            # Create new price
            price = Price(
                product_id=product.id,
                supermarket_id=self.supermarket.id,
                price=product_data["price"],
                original_price=product_data.get("original_price"),
                is_promotion=product_data.get("is_promotion", False),
                promotion_label=product_data.get("promotion_label"),
                promotion_end_date=product_data.get("promotion_end_date"),
                currency=product_data.get("currency", "EUR"),
                source_url=product_data.get("source_url"),
                scraped_at=self.scraped_at,
                is_available=product_data.get("is_available", True),
            )
            db.add(price)
        
        # Create price history
        history = PriceHistory(
            product_id=product.id,
            supermarket_id=self.supermarket.id,
            price=product_data["price"],
            original_price=product_data.get("original_price"),
            is_promotion=product_data.get("is_promotion", False),
            recorded_at=self.scraped_at,
        )
        db.add(history)
        
        await db.commit()
        await db.refresh(product)
        
        return product, price, is_new


def get_scraper(supermarket_id: int):
    """Get scraper class for supermarket."""
    from app.scraping.mock import CarrefourScraper, LeclercScraper, AuchanScraper
    
    scrapers = {
        1: CarrefourScraper,
        2: LeclercScraper,
        3: AuchanScraper,
    }
    
    return scrapers.get(supermarket_id)