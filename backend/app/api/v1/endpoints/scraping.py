from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.scraping_job import ScrapingJob
from app.models.supermarket import Supermarket
from app.models.user import User
from app.scraping import ScrapingService, get_scraper
from app.schemas import ScrapingJobCreate, ScrapingJobResponse

router = APIRouter()


@router.get("/jobs", response_model=list[ScrapingJobResponse])
async def list_scraping_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(ScrapingJob).order_by(ScrapingJob.created_at.desc()))
    jobs = result.scalars().all()

    response = []
    for job in jobs:
        sm_result = await db.execute(select(Supermarket).where(Supermarket.id == job.supermarket_id))
        supermarket = sm_result.scalar_one_or_none()
        item = ScrapingJobResponse.model_validate(job)
        item.supermarket_name = supermarket.name if supermarket else "Unknown"
        response.append(item)

    return response


@router.post("/jobs", response_model=ScrapingJobResponse, status_code=201)
async def create_scraping_job(
    job_in: ScrapingJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    # Check if supermarket exists
    sm_result = await db.execute(select(Supermarket).where(Supermarket.id == job_in.supermarket_id))
    supermarket = sm_result.scalar_one_or_none()
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket not found")

    # Check if scraper exists
    if not get_scraper(job_in.supermarket_id):
        raise HTTPException(status_code=400, detail="No scraper configured for this supermarket")

    # Check if job is already running
    running_result = await db.execute(
        select(ScrapingJob).where(
            ScrapingJob.supermarket_id == job_in.supermarket_id,
            ScrapingJob.status == "running"
        )
    )
    if running_result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Scraping job already running for this supermarket")

    job = ScrapingJob(supermarket_id=job_in.supermarket_id)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Start scraping in background
    from app.tasks.scraping_tasks import run_scraping_job
    run_scraping_job.delay(job.id)

    response = ScrapingJobResponse.model_validate(job)
    response.supermarket_name = supermarket.name
    return response


@router.get("/jobs/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Scraping job not found")

    sm_result = await db.execute(select(Supermarket).where(Supermarket.id == job.supermarket_id))
    supermarket = sm_result.scalar_one_or_none()
    response = ScrapingJobResponse.model_validate(job)
    response.supermarket_name = supermarket.name if supermarket else "Unknown"
    return response


@router.get("/config/{supermarket_id}")
async def get_scraping_config(
    supermarket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    scraper_class = get_scraper(supermarket_id)
    if not scraper_class:
        raise HTTPException(status_code=404, detail="No scraper configured for this supermarket")

    # Return config structure
    return {
        "supermarket_id": supermarket_id,
        "scraper": scraper_class.__name__,
        "rate_limit": {"min": 2, "max": 5},
    }