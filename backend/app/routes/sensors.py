import random
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import db_models
from app.models.schemas import IoTTelemetryInput, IoTStatusResponse
from app.services.mqtt_service import (
    latest_iot_data,
    iot_metadata,
    process_telemetry_reading,
)

router = APIRouter(tags=["sensors"])


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


@router.post("/iot/telemetry")
def ingest_telemetry(payload: IoTTelemetryInput, db: Session = Depends(get_db)):
    """
    Ingest live telemetry from real-world IoT microcontrollers (ESP32, ESP8266, Arduino)
    over HTTP REST POST. Automatically updates in-memory dashboard data and persists to SQLite.
    """
    data_dict = payload.model_dump(exclude_none=True)
    if not data_dict:
        raise HTTPException(status_code=400, detail="Empty telemetry payload received")

    # Ingest and persist
    updated = process_telemetry_reading(data_dict, source="http_rest", persist_db=True)

    return {
        "status": "success",
        "message": "Telemetry received and persisted successfully",
        "device_id": iot_metadata["device_id"],
        "timestamp": iot_metadata["last_packet_time"],
        "data": updated,
    }


@router.get("/iot/live")
def get_live_data(
    simulate: bool = Query(
        False,
        description="Set to true only if you want to simulate random sensor fluctuations.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieves the latest IoT telemetry reading.
    By default returns true real-world hardware readings without random perturbation.
    """
    if simulate:
        latest_iot_data["temperature"] = round(
            clamp(latest_iot_data["temperature"] + random.uniform(-0.5, 0.5), 10, 50), 1
        )
        latest_iot_data["humidity"] = round(
            clamp(latest_iot_data["humidity"] + random.uniform(-1.0, 1.0), 20, 60), 1
        )
        latest_iot_data["ph"] = round(
            clamp(latest_iot_data["ph"] + random.uniform(-0.05, 0.05), 3, 10), 2
        )
        latest_iot_data["rainfall"] = round(
            clamp(latest_iot_data["rainfall"] + random.uniform(-1.5, 1.5), 40, 60), 1
        )
        latest_iot_data["tds"] = round(
            clamp(latest_iot_data.get("tds", 150.0) + random.uniform(-2, 2), 0, 500), 1
        )

        new_reading = db_models.SensorReading(
            temperature=latest_iot_data["temperature"],
            humidity=latest_iot_data["humidity"],
            ph=latest_iot_data["ph"],
            rainfall=latest_iot_data["rainfall"],
            n=latest_iot_data["N"],
            p=latest_iot_data["P"],
            k=latest_iot_data["K"],
            tds=latest_iot_data["tds"],
        )
        db.add(new_reading)
        db.commit()

    return {
        "status": "success",
        "data": latest_iot_data,
        "metadata": iot_metadata,
    }


@router.get("/iot/status")
def get_iot_status():
    """
    Check real-world IoT device connection health, broker, and last received packet timestamp.
    """
    is_active = False
    if iot_metadata.get("last_packet_time"):
        try:
            last_dt = datetime.fromisoformat(iot_metadata["last_packet_time"])
            # Consider active if a packet was received within the last 120 seconds
            is_active = (datetime.utcnow() - last_dt).total_seconds() < 120
        except Exception:
            is_active = iot_metadata.get("connected", False)

    return {
        "status": "success",
        "connected": is_active,
        "device_id": iot_metadata.get("device_id", "esp32-node-01"),
        "source": iot_metadata.get("source", "standby"),
        "last_packet_time": iot_metadata.get("last_packet_time"),
        "packet_count": iot_metadata.get("packet_count", 0),
        "broker": iot_metadata.get("broker"),
        "topic": iot_metadata.get("topic"),
        "data": latest_iot_data,
    }


@router.get("/iot/history")
def get_sensor_history(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    """
    Retrieves historical telemetry readings saved in the database.
    """
    readings = (
        db.query(db_models.SensorReading)
        .order_by(db_models.SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )

    history = [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "ph": r.ph,
            "rainfall": r.rainfall,
            "N": r.n,
            "P": r.p,
            "K": r.k,
            "tds": r.tds,
        }
        for r in readings
    ]
    return {"status": "success", "count": len(history), "data": history}
