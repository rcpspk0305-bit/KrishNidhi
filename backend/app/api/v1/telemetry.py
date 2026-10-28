from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.api.deps import get_current_device
from app.models.db_models import Device, SensorReading, Alert, PlantProfile
from app.schemas.plant_monitor_schemas import (
    TelemetryCreate,
    TelemetryResponse,
    TelemetryHistoryResponse,
)
from app.services.sse_service import sse_manager

router = APIRouter(prefix="/devices", tags=["Telemetry"])

@router.post("/{device_id}/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    device_id: str,
    payload: TelemetryCreate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """
    Ingests environmental and system telemetry from the ESP8266 NodeMCU.
    Validates readings, updates device state, checks threshold alerts,
    and broadcasts real-time SSE updates to connected dashboards.
    """
    now = datetime.now(timezone.utc)

    # 1. Update device connectivity & reported state
    device.last_seen = now
    device.status = "online"
    device.pump_state = payload.pump_on
    if payload.control_mode:
        device.control_mode = payload.control_mode

    # 2. Persist Sensor Reading
    reading = SensorReading(
        device_id=device.id,
        timestamp=now,
        temperature=payload.temperature,
        humidity=payload.humidity,
        soil_moisture=payload.soil_moisture,
        soil_raw=payload.soil_raw,
        motion_detected=payload.motion_detected,
        pump_on=payload.pump_on,
        control_mode=payload.control_mode,
    )
    db.add(reading)
    db.flush()

    # 3. Check for Threshold Alerts
    profile = db.query(PlantProfile).filter(PlantProfile.device_id == device.id).first()
    min_moisture = profile.preferred_moisture_min if profile else 30.0
    max_temp = profile.preferred_temp_max if profile else 32.0

    # Low Soil Moisture Alert
    if payload.soil_moisture is not None and payload.soil_moisture < min_moisture:
        # Check if active unacknowledged alert already exists
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.device_id == device.id,
                Alert.type == "SOIL_DRY",
                Alert.acknowledged == False,
            )
            .first()
        )
        if not existing_alert:
            new_alert = Alert(
                device_id=device.id,
                type="SOIL_DRY",
                severity="high" if payload.soil_moisture < 15.0 else "medium",
                message=f"Critically dry soil: {payload.soil_moisture:.1f}% is below minimum threshold ({min_moisture:.0f}%).",
                acknowledged=False,
                timestamp=now,
            )
            db.add(new_alert)

    # High Temperature Alert
    if payload.temperature is not None and payload.temperature > max_temp:
        existing_temp_alert = (
            db.query(Alert)
            .filter(
                Alert.device_id == device.id,
                Alert.type == "HIGH_TEMP",
                Alert.acknowledged == False,
            )
            .first()
        )
        if not existing_temp_alert:
            t_alert = Alert(
                device_id=device.id,
                type="HIGH_TEMP",
                severity="medium",
                message=f"High ambient temperature: {payload.temperature:.1f}°C exceeds threshold ({max_temp:.1f}°C).",
                acknowledged=False,
                timestamp=now,
            )
            db.add(t_alert)

    # PIR Motion Detected notification
    if payload.motion_detected:
        existing_motion = (
            db.query(Alert)
            .filter(
                Alert.device_id == device.id,
                Alert.type == "MOTION_ALERT",
                Alert.acknowledged == False,
            )
            .first()
        )
        if not existing_motion:
            m_alert = Alert(
                device_id=device.id,
                type="MOTION_ALERT",
                severity="low",
                message="PIR sensor detected activity near the plant planter.",
                acknowledged=False,
                timestamp=now,
            )
            db.add(m_alert)

    db.commit()
    db.refresh(reading)

    # 4. Broadcast real-time SSE event to all connected dashboard clients
    event_payload = {
        "device_id": device.id,
        "timestamp": reading.timestamp.isoformat(),
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "soil_moisture": reading.soil_moisture,
        "soil_raw": reading.soil_raw,
        "motion_detected": reading.motion_detected,
        "pump_on": reading.pump_on,
        "control_mode": reading.control_mode,
        "device_status": device.status,
    }
    await sse_manager.broadcast("telemetry", event_payload, device_id=device.id)

    return reading

@router.get("/{device_id}/telemetry/latest", response_model=TelemetryResponse)
def get_latest_telemetry(device_id: str, db: Session = Depends(get_db)):
    """Retrieves the most recent sensor reading for the specified device."""
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No telemetry readings found for this device",
        )
    return reading

@router.get("/{device_id}/telemetry/history", response_model=TelemetryHistoryResponse)
def get_telemetry_history(
    device_id: str,
    limit: int = Query(50, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Retrieves chronological sensor telemetry data over a specified time window
    (default: last 24 hours, up to 500 records) for trend visualization.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id, SensorReading.timestamp >= cutoff)
        .order_by(SensorReading.timestamp.asc())
        .limit(limit)
        .all()
    )

    return TelemetryHistoryResponse(
        device_id=device_id,
        total_records=len(readings),
        readings=readings,
    )
