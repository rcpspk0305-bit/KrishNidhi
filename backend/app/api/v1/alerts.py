from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.db_models import Alert
from app.schemas.plant_monitor_schemas import AlertResponse

router = APIRouter(tags=["Alerts"])

@router.get("/devices/{device_id}/alerts", response_model=List[AlertResponse])
def get_device_alerts(
    device_id: str,
    unacknowledged_only: bool = Query(False, description="Filter only unacknowledged alerts"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieves security, sensor, and threshold alerts for a given device."""
    query = db.query(Alert).filter(Alert.device_id == device_id)
    if unacknowledged_only:
        query = query.filter(Alert.acknowledged == False)

    alerts = query.order_by(desc(Alert.timestamp)).limit(limit).all()
    return alerts

@router.patch("/alerts/{id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(id: int, db: Session = Depends(get_db)):
    """Marks an active environmental or hardware alert as reviewed and acknowledged."""
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert
