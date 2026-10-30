import os
import secrets
from datetime import datetime, timezone
from typing import Literal, Optional, Dict, Any
from fastapi import APIRouter, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, text

from app.core.database import get_db
from app.models.db_models import Device, SensorReading, PumpEvent, Alert, PlantProfile
from app.core.security import hash_api_key
from app.services.sse_service import sse_manager

router = APIRouter(tags=["Device Compatibility & Direct Control"])

DEVICE_TOKEN = os.environ.get("DEVICE_TOKEN", "replace-with-a-long-random-secret")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "super_secret_admin_token_2026")

# In-memory command sequencing for ESP8266 REST polling
_command_state: Dict[str, Dict[str, Any]] = {
    "plant-01": {"command_id": 0, "mode": "auto", "pump_on": False},
    "esp8266-plant-01": {"command_id": 0, "mode": "auto", "pump_on": False},
}


class DeviceTelemetry(BaseModel):
    device_id: str = "plant-01"
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    soil_raw: Optional[int] = None
    soil_moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    motion: bool = False
    pump_on: bool = False
    mode: Literal["auto", "manual", "off"] = "auto"


class DeviceControl(BaseModel):
    device_id: str = "plant-01"
    mode: Literal["auto", "manual"]
    pump_on: bool = False


def verify_token(provided: str, expected: str):
    """Constant-time token validation."""
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


def get_or_create_device(device_id: str, db: Session) -> Device:
    """Finds or auto-provisions device and plant profile in the database."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        device = Device(
            id=device_id,
            name=f"Smart Plant Monitor ({device_id})",
            api_key_hash=hash_api_key(DEVICE_TOKEN),
            status="online",
            control_mode="AUTO",
            pump_state=False,
            last_seen=datetime.now(timezone.utc),
        )
        db.add(device)
        db.flush()

        profile = PlantProfile(
            device_id=device.id,
            plant_name="Monstera Deliciosa",
            plant_type="Tropical Foliage",
            preferred_temp_min=18.0,
            preferred_temp_max=30.0,
            preferred_humidity_min=50.0,
            preferred_humidity_max=75.0,
            preferred_moisture_min=30.0,
            preferred_moisture_max=60.0,
        )
        db.add(profile)
        db.commit()
        db.refresh(device)
    return device


@router.post("/device/telemetry")
async def receive_device_telemetry(
    data: DeviceTelemetry,
    x_device_token: str = Header(default="", alias="X-Device-Token"),
    x_device_key: Optional[str] = Header(None, alias="X-Device-Key"),
    db: Session = Depends(get_db),
):
    """
    Receives ESP8266 telemetry, persists it to SQLite database,
    updates last_seen and online status, evaluates alerts,
    and broadcasts updates via SSE to the dashboard.
    """
    token_to_check = x_device_token or x_device_key or ""
    verify_token(token_to_check, DEVICE_TOKEN)

    now = datetime.now(timezone.utc)
    device = get_or_create_device(data.device_id, db)

    # Update device online state
    device.last_seen = now
    device.status = "online"
    device.pump_state = data.pump_on
    device.control_mode = data.mode.upper()

    # Persist sensor reading
    reading = SensorReading(
        device_id=device.id,
        timestamp=now,
        temperature=data.temperature_c,
        humidity=data.humidity_pct,
        soil_moisture=data.soil_moisture_pct,
        soil_raw=data.soil_raw,
        motion_detected=data.motion,
        pump_on=data.pump_on,
        control_mode=data.mode.upper(),
    )
    db.add(reading)

    # Check alert conditions
    if data.soil_moisture_pct is not None and data.soil_moisture_pct < 30.0:
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
            db.add(
                Alert(
                    device_id=device.id,
                    type="SOIL_DRY",
                    severity="high" if data.soil_moisture_pct < 15.0 else "medium",
                    message=f"Critically dry soil: {data.soil_moisture_pct:.1f}% is below 30% threshold.",
                    acknowledged=False,
                    timestamp=now,
                )
            )

    db.commit()
    db.refresh(reading)

    # Broadcast to web dashboard via SSE
    await sse_manager.broadcast(
        "telemetry",
        {
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
        },
        device_id=device.id,
    )

    return {"success": True, "device_id": device.id, "timestamp": now.isoformat()}


@router.get("/device/command")
def get_device_command(
    device_id: str = "plant-01",
    x_device_token: str = Header(default="", alias="X-Device-Token"),
    x_device_key: Optional[str] = Header(None, alias="X-Device-Key"),
    db: Session = Depends(get_db),
):
    """
    Returns the pending command for the ESP8266 NodeMCU.
    Supports command sequencing with incremental integer command_id.
    """
    token_to_check = x_device_token or x_device_key or ""
    verify_token(token_to_check, DEVICE_TOKEN)

    # Ensure device exists
    get_or_create_device(device_id, db)

    cmd = _command_state.get(device_id)
    if not cmd:
        cmd = {"command_id": 0, "mode": "auto", "pump_on": False}
        _command_state[device_id] = cmd

    return cmd


@router.get("/state")
def get_system_state(
    device_id: str = "plant-01",
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    """
    Returns latest sensor values, device connection status,
    online/offline detection, confirmed pump state, and pending command state.
    """
    if x_admin_token:
        verify_token(x_admin_token, ADMIN_TOKEN)

    device = get_or_create_device(device_id, db)
    now = datetime.now(timezone.utc)

    # Online/offline detection based on last_seen within 35 seconds
    is_online = False
    seconds_ago = None
    if device.last_seen:
        last_seen_dt = device.last_seen
        if last_seen_dt.tzinfo is None:
            last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
        seconds_ago = max(0.0, (now - last_seen_dt).total_seconds())
        is_online = seconds_ago <= 35.0

    device.status = "online" if is_online else "offline"
    db.commit()

    # Latest reading
    latest = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device.id)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )

    latest_dict = None
    if latest:
        latest_dict = {
            "temperature_c": latest.temperature,
            "humidity_pct": latest.humidity,
            "soil_raw": latest.soil_raw,
            "soil_moisture_pct": latest.soil_moisture,
            "motion": bool(latest.motion_detected),
            "pump_on": bool(latest.pump_on),
            "mode": (latest.control_mode or "auto").lower(),
            "timestamp": latest.timestamp.isoformat() if latest.timestamp else None,
        }

    cmd = _command_state.get(device.id, {"command_id": 0, "mode": "auto", "pump_on": False})

    return {
        "device_id": device.id,
        "online": is_online,
        "last_seen": device.last_seen.isoformat() if device.last_seen else None,
        "seconds_since_last_seen": seconds_ago,
        "pump_on": bool(device.pump_state),
        "mode": (device.control_mode or "auto").lower(),
        "telemetry": latest_dict,
        "command": cmd,
    }


@router.post("/control")
async def set_system_control(
    control: DeviceControl,
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    """
    Allows authenticated users / dashboard to change pump mode and actuation state.
    Updates command queue, logs a PumpEvent, and broadcasts SSE update.
    """
    verify_token(x_admin_token, ADMIN_TOKEN)

    device = get_or_create_device(control.device_id, db)
    now = datetime.now(timezone.utc)

    cmd = _command_state.setdefault(
        device.id, {"command_id": 0, "mode": "auto", "pump_on": False}
    )
    cmd["command_id"] += 1
    cmd["mode"] = control.mode
    cmd["pump_on"] = control.pump_on if control.mode == "manual" else False

    # Log pump event audit record
    pump_event = PumpEvent(
        device_id=device.id,
        requested_state=cmd["pump_on"],
        confirmed_state=bool(device.pump_state),
        source="web_control",
        control_mode=control.mode.upper(),
        reason=f"Control command {cmd['command_id']} issued via /api/control",
        timestamp=now,
    )
    db.add(pump_event)
    db.commit()

    # Broadcast command to connected dashboards
    await sse_manager.broadcast(
        "command_created",
        {
            "command_id": cmd["command_id"],
            "device_id": device.id,
            "mode": cmd["mode"],
            "pump_on": cmd["pump_on"],
        },
        device_id=device.id,
    )

    return cmd
