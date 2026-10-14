from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.services import AlertService
from app.scraping import ScrapingService

settings = get_settings()

# Create async engine for Celery tasks
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(name="app.tasks.alert_tasks.check_alerts")
def check_alerts():
    """Check all active alerts for price drops."""
    import asyncio
    
    async def _check():
        async with AsyncSessionLocal() as db:
            service = AlertService()
            triggered = await service.check_alerts(db)
            return f"Checked alerts, triggered {len(triggered)} alerts"
    
    return asyncio.run(_check())


@shared_task(name="app.tasks.scraping_tasks.run_scraping_job")
def run_scraping_job(job_id: int):
    """Run a scraping job."""
    import asyncio
    
    async def _run():
        async with AsyncSessionLocal() as db:
            service = ScrapingService()
            result = await service.run_scraping_job(job_id, db)
            return result
    
    return asyncio.run(_run())