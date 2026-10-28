import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.api.deps import get_current_device
from app.models.db_models import Device, DeviceCommand, PumpEvent
from app.schemas.plant_monitor_schemas import (
    PumpControlRequest,
    DeviceCommandItem,
    CommandPollResponse,
    CommandAckRequest,
    CommandAckResponse,
    PumpEventResponse,
)
from app.services.sse_service import sse_manager

router = APIRouter(prefix="/devices", tags=["Pump Control"])

@router.post("/{device_id}/pump", response_model=DeviceCommandItem)
async def request_pump_control(
    device_id: str,
    payload: PumpControlRequest,
    db: Session = Depends(get_db),
):
    """
    Submits a remote actuation or mode change request to the target ESP8266.
    Generates a unique, non-duplicable command with a TTL expiration window.
    The server does not claim the physical pump turned on until the ESP8266
    confirms execution via an acknowledgment.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    now = datetime.now(timezone.utc)
    ttl = payload.ttl_seconds or 60
    expires = now + timedelta(seconds=ttl)

    # Convert value to standardized string
    val_str = str(payload.value).strip()
    if payload.action == "SET_PUMP":
        val_lower = val_str.lower()
        if val_lower not in ["true", "false", "1", "0", "on", "off"]:
            raise HTTPException(
                status_code=400,
                detail="Value for SET_PUMP must be boolean or 'on'/'off'",
            )
        val_str = "true" if val_lower in ["true", "1", "on"] else "false"
    elif payload.action == "SET_MODE":
        val_upper = val_str.upper()
        if val_upper not in ["AUTO", "MANUAL", "OFF"]:
            raise HTTPException(
                status_code=400,
                detail="Value for SET_MODE must be 'AUTO', 'MANUAL', or 'OFF'",
            )
        val_str = val_upper

    cmd_id = f"cmd_{uuid.uuid4().hex[:12]}"
    command = DeviceCommand(
        id=cmd_id,
        device_id=device.id,
        action=payload.action,
        value=val_str,
        status="PENDING",
        created_at=now,
        expires_at=expires,
    )
    db.add(command)

    # Log initial requested pump event
    if payload.action == "SET_PUMP":
        requested_bool = (val_str == "true")
        pe = PumpEvent(
            device_id=device.id,
            requested_state=requested_bool,
            confirmed_state=bool(device.pump_state),
            source="web_command",
            control_mode=device.control_mode or "AUTO",
            reason=f"Command {cmd_id} issued by operator",
            timestamp=now,
        )
        db.add(pe)

    db.commit()
    db.refresh(command)

    # Notify dashboard of pending command
    await sse_manager.broadcast(
        "command_created",
        {
            "command_id": command.id,
            "action": command.action,
            "value": command.value,
            "status": command.status,
            "device_id": device.id,
        },
        device_id=device.id,
    )

    return DeviceCommandItem(
        command_id=command.id,
        action=command.action,
        value=command.value,
        created_at=command.created_at,
        expires_at=command.expires_at,
        status=command.status,
    )

@router.get("/{device_id}/commands", response_model=CommandPollResponse)
def poll_pending_commands(
    device_id: str,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """
    Endpoint polled regularly by the ESP8266 (e.g. every 2 seconds).
    Automatically expires stale commands and returns the next valid pending command.
    """
    now = datetime.now(timezone.utc)

    # 1. Expire outdated pending commands
    expired_cmds = (
        db.query(DeviceCommand)
        .filter(
            DeviceCommand.device_id == device.id,
            DeviceCommand.status == "PENDING",
            DeviceCommand.expires_at < now,
        )
        .all()
    )
    for exp in expired_cmds:
        exp.status = "EXPIRED"
        exp.error_message = "Command expired before device retrieved it"

    if expired_cmds:
        db.commit()

    # 2. Fetch oldest unexpired pending command
    pending = (
        db.query(DeviceCommand)
        .filter(
            DeviceCommand.device_id == device.id,
            DeviceCommand.status == "PENDING",
            DeviceCommand.expires_at >= now,
        )
        .order_by(DeviceCommand.created_at.asc())
        .first()
    )

    if not pending:
        return CommandPollResponse(has_command=False, command=None, command_id=None, pump=None, mode=None)

    cmd_item = DeviceCommandItem(
        command_id=pending.id,
        action=pending.action,
        value=pending.value,
        created_at=pending.created_at,
        expires_at=pending.expires_at,
        status=pending.status,
    )

    pump_val = None
    mode_val = None
    if pending.action == "SET_PUMP":
        pump_val = str(pending.value).lower() in ["true", "1", "on"]
    elif pending.action == "SET_MODE":
        mode_val = str(pending.value).upper()

    return CommandPollResponse(
        has_command=True,
        command=cmd_item,
        command_id=pending.id,
        pump=pump_val,
        mode=mode_val,
    )

@router.post("/{device_id}/commands/{command_id}/ack", response_model=CommandAckResponse)
async def acknowledge_command(
    device_id: str,
    command_id: str,
    payload: CommandAckRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """
    Called by the ESP8266 after attempting to execute a command.
    Reports physical verification (e.g. relay engaged/disengaged, safety lockout rejected).
    Updates confirmed state and broadcasts to dashboard.
    """
    now = datetime.now(timezone.utc)

    command = (
        db.query(DeviceCommand)
        .filter(DeviceCommand.id == command_id, DeviceCommand.device_id == device.id)
        .first()
    )
    if not command:
        raise HTTPException(status_code=404, detail="Command ID not found for this device")

    command.status = payload.status
    command.executed_at = now
    if payload.reason:
        command.error_message = payload.reason

    # If pump state was confirmed, update device record
    if payload.confirmed_state is not None:
        device.pump_state = payload.confirmed_state

    if command.action == "SET_MODE" and payload.status == "APPLIED":
        device.control_mode = command.value

    # Record confirmed pump event
    pe = PumpEvent(
        device_id=device.id,
        requested_state=(command.value == "true") if command.action == "SET_PUMP" else bool(device.pump_state),
        confirmed_state=bool(payload.confirmed_state) if payload.confirmed_state is not None else bool(device.pump_state),
        source="esp8266_ack",
        control_mode=device.control_mode or "AUTO",
        reason=f"Ack {payload.status}: {payload.reason or 'executed'}",
        timestamp=now,
    )
    db.add(pe)

    db.commit()

    # Broadcast state change to all dashboards via SSE
    await sse_manager.broadcast(
        "pump_state_updated",
        {
            "device_id": device.id,
            "command_id": command.id,
            "action": command.action,
            "status": payload.status,
            "confirmed_state": device.pump_state,
            "control_mode": device.control_mode,
            "reason": payload.reason,
            "timestamp": now.isoformat(),
        },
        device_id=device.id,
    )

    return CommandAckResponse(
        command_id=command.id,
        status=payload.status,
        confirmed_state=device.pump_state,
        message=f"Command {command_id} acknowledged as {payload.status}",
    )

@router.get("/{device_id}/pump/history", response_model=List[PumpEventResponse])
def get_pump_history(
    device_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Returns the chronological record of pump actuation events (source, requested, confirmed, reason).
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    events = (
        db.query(PumpEvent)
        .filter(PumpEvent.device_id == device.id)
        .order_by(desc(PumpEvent.timestamp))
        .limit(limit)
        .all()
    )
    return events
