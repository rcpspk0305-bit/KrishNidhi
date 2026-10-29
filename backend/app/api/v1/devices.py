from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_api_key, generate_device_api_key
from app.models.db_models import Device, PlantProfile, Alert, PumpEvent
from app.schemas.plant_monitor_schemas import (
    DeviceCreate,
    DeviceResponse,
    DeviceStatusResponse,
    PlantProfileUpdate,
    PlantProfileResponse,
)

router = APIRouter(prefix="/devices", tags=["Devices"])

@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    """Registers a new ESP8266 device and returns its device credentials."""
    existing = db.query(Device).filter(Device.id == payload.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with id '{payload.id}' already exists",
        )

    raw_api_key = payload.api_key or generate_device_api_key()
    hashed_key = hash_api_key(raw_api_key)

    device = Device(
        id=payload.id,
        name=payload.name,
        api_key_hash=hashed_key,
        status="offline",
        control_mode="AUTO",
        pump_state=False,
    )
    db.add(device)
    db.flush()

    # Create associated default plant profile
    profile = PlantProfile(
        device_id=device.id,
        plant_name="Cherry Tomato",
        plant_type="Vegetable",
        preferred_temp_min=20.0,
        preferred_temp_max=32.0,
        preferred_humidity_min=50.0,
        preferred_humidity_max=75.0,
        preferred_moisture_min=30.0,
        preferred_moisture_max=60.0,
    )
    db.add(profile)
    db.commit()
    db.refresh(device)

    resp = DeviceResponse.model_validate(device)
    resp.api_key = raw_api_key  # Returned once upon registration
    return resp

@router.get("", response_model=List[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    """Lists all registered devices."""
    devices = db.query(Device).all()
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, db: Session = Depends(get_db)):
    """Retrieves metadata and current configuration for a specific device."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.get("/{device_id}/status", response_model=DeviceStatusResponse)
def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """
    Evaluates real-time device connectivity.
    A device is considered online if telemetry was received within the last 30 seconds.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    now = datetime.now(timezone.utc)
    seconds_ago = None
    is_online = False

    if device.last_seen:
        last_seen = device.last_seen
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        seconds_ago = round((now - last_seen).total_seconds(), 1)
        is_online = seconds_ago <= 30.0

    active_alerts = (
        db.query(Alert)
        .filter(Alert.device_id == device_id, Alert.acknowledged == False)
        .count()
    )

    last_pump_event = (
        db.query(PumpEvent)
        .filter(PumpEvent.device_id == device_id, PumpEvent.confirmed_state == True)
        .order_by(PumpEvent.timestamp.desc())
        .first()
    )
    last_watering = last_pump_event.timestamp if last_pump_event else None
    pump_runtime = 0
    if device.pump_state and last_pump_event and last_pump_event.timestamp:
        event_time = last_pump_event.timestamp
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        pump_runtime = int(max(0, (now - event_time).total_seconds()))

    return DeviceStatusResponse(
        device_id=device.id,
        status="online" if is_online else "offline",
        online=is_online,
        control_mode=device.control_mode or "AUTO",
        pump_state=bool(device.pump_state),
        last_seen=device.last_seen,
        seconds_since_last_seen=seconds_ago,
        sensor_fault=False,
        active_alerts_count=active_alerts,
        last_watering_time=last_watering,
        pump_runtime_seconds=pump_runtime,
    )

@router.get("/{device_id}/profile", response_model=PlantProfileResponse)
def get_plant_profile(device_id: str, db: Session = Depends(get_db)):
    """Retrieves target environmental profile and calibrated moisture thresholds."""
    profile = db.query(PlantProfile).filter(PlantProfile.device_id == device_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Plant profile not found")
    return profile

@router.put("/{device_id}/profile", response_model=PlantProfileResponse)
def update_plant_profile(device_id: str, payload: PlantProfileUpdate, db: Session = Depends(get_db)):
    """Updates target environmental thresholds for automated irrigation decisions."""
    profile = db.query(PlantProfile).filter(PlantProfile.device_id == device_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Plant profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
