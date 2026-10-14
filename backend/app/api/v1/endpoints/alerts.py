from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.price_alert import PriceAlert
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.user import User
from app.services import AlertService
from app.schemas import (
    PriceAlertCreate,
    PriceAlertUpdate,
    PriceAlertResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService()
    alerts = await service.get_user_alerts(current_user.id, db)
    
    if is_active is not None:
        alerts = [a for a in alerts if a.is_active == is_active]
    
    total = len(alerts)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_alerts = alerts[start:end]

    return {
        "items": [PriceAlertResponse.model_validate(a) for a in paginated_alerts],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=PriceAlertResponse, status_code=201)
async def create_alert(
    alert_in: PriceAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService()
    try:
        alert = await service.create_alert(current_user.id, alert_in.model_dump(), db)
        return alert
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{alert_id}", response_model=PriceAlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService()
    alerts = await service.get_user_alerts(current_user.id, db)
    alert = next((a for a in alerts if a.id == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=PriceAlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: PriceAlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService()
    update_data = alert_update.model_dump(exclude_unset=True)
    alert = await service.update_alert(alert_id, current_user.id, update_data, db)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AlertService()
    deleted = await service.delete_alert(alert_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")