from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(name="app.tasks.cleanup_tasks.cleanup_old_prices")
def cleanup_old_prices():
    """Clean up old price history older than 1 year."""
    import asyncio
    from datetime import datetime, UTC, timedelta
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            from app.models.price_history import PriceHistory
            from sqlalchemy import delete
            
            cutoff = datetime.now(UTC) - timedelta(days=365)
            result = await db.execute(
                delete(PriceHistory).where(PriceHistory.recorded_at < cutoff)
            )
            await db.commit()
            return f"Deleted {result.rowcount} old price history records"
    
    return asyncio.run(_cleanup())


@shared_task(name="app.tasks.cleanup_tasks.cleanup_old_scraping_jobs")
def cleanup_old_scraping_jobs():
    """Clean up old scraping jobs older than 30 days."""
    import asyncio
    from datetime import datetime, UTC, timedelta
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            from app.models.scraping_job import ScrapingJob
            from sqlalchemy import delete
            
            cutoff = datetime.now(UTC) - timedelta(days=30)
            result = await db.execute(
                delete(ScrapingJob).where(ScrapingJob.created_at < cutoff)
            )
            await db.commit()
            return f"Deleted {result.rowcount} old scraping jobs"
    
    return asyncio.run(_cleanup())