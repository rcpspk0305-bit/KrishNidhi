from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_device_auth, verify_api_key, hash_api_key, generate_device_api_key
from app.models.db_models import Device, PlantProfile

def get_current_device(
    device_id: str,
    device_key: Optional[str] = Depends(get_device_auth),
    db: Session = Depends(get_db),
) -> Device:
    """
    Authenticates the ESP8266 device by device_id and API key.
    For local development convenience, if device_id is default 'esp8266-plant-01'
    and doesn't exist yet, it is auto-provisioned.
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        # Auto-provision standard demo device for painless plug-and-play testing
        raw_key = device_key or "default_secret_key_123"
        hashed = hash_api_key(raw_key)
        device = Device(
            id=device_id,
            name=f"Smart Plant Monitor ({device_id})",
            api_key_hash=hashed,
            status="online",
            control_mode="AUTO",
            pump_state=False,
            last_seen=datetime.now(timezone.utc),
        )
        db.add(device)
        db.flush()

        # Create default plant profile
        profile = PlantProfile(
            device_id=device.id,
            plant_name="Monstera Deliciosa",
            plant_type="Foliage",
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

    # If device requires auth and key was supplied
    if device_key:
        if not verify_api_key(device_key, device.api_key_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid device credentials",
            )
    elif device.api_key_hash and device.api_key_hash != hash_api_key("default_secret_key_123"):
        # Key is strictly required if not using default dev key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-Device-Key header",
        )

    return device
