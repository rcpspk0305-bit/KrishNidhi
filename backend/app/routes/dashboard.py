from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import db_models
from app.models.schemas import (
    DashboardMetric,
    DashboardOverviewResponse,
    DashboardWindow,
    DashboardWindowResponse,
    TrendPoint,
    SensorData,
)
from app.services.mqtt_service import latest_iot_data
from app.services.ml_service import predict_crop

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _latest_readings(db: Session, limit: int = 24) -> List[db_models.SensorReading]:
    return (
        db.query(db_models.SensorReading)
        .order_by(db_models.SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )


def _build_trend_points(readings: List[db_models.SensorReading]) -> List[TrendPoint]:
    if not readings:
        now = datetime.utcnow()
        return [
            TrendPoint(
                slot=(now.replace(minute=0, second=0, microsecond=0)).strftime("%H:%M"),
                temperature=round(float(latest_iot_data.get("temperature", 25.5)), 1),
                humidity=round(float(latest_iot_data.get("humidity", 40.0)), 1),
            )
        ]

    points: List[TrendPoint] = []
    for row in reversed(readings):
        points.append(
            TrendPoint(
                slot=row.timestamp.strftime("%H:%M"),
                temperature=round(float(row.temperature), 1),
                humidity=round(float(row.humidity), 1),
            )
        )
    return points


@router.get("/central", response_model=DashboardOverviewResponse)
def central_dashboard(db: Session = Depends(get_db)):
    readings = _latest_readings(db)

    if readings:
        avg_temp = sum(float(r.temperature) for r in readings) / len(readings)
        avg_hum = sum(float(r.humidity) for r in readings) / len(readings)
        avg_rain = sum(float(r.rainfall) for r in readings) / len(readings)
        avg_ph = sum(float(r.ph) for r in readings) / len(readings)
    else:
        avg_temp = float(latest_iot_data.get("temperature", 25.5))
        avg_hum = float(latest_iot_data.get("humidity", 40.0))
        avg_rain = float(latest_iot_data.get("rainfall", 50.0))
        avg_ph = float(latest_iot_data.get("ph", 6.8))

    health_score = int(
        max(
            20,
            min(
                98,
                round(
                    (
                        float(latest_iot_data.get("N", 88))
                        + float(latest_iot_data.get("P", 50))
                        + float(latest_iot_data.get("K", 42))
                    )
                    / 3
                ),
            ),
        )
    )

    metrics = [
        DashboardMetric(label="Avg Temperature", value=round(avg_temp, 1), unit="C", trend=2.1),
        DashboardMetric(label="Avg Humidity", value=round(avg_hum, 1), unit="%", trend=1.4),
        DashboardMetric(label="Avg Rainfall", value=round(avg_rain, 1), unit="mm", trend=-0.7),
        DashboardMetric(label="Avg Soil pH", value=round(avg_ph, 2), unit="", trend=0.3),
    ]

    windows = [
        DashboardWindow(
            id="overview",
            title="Overview Window",
            status="active",
            summary="Real-time crop recommendation and sensor cards.",
        ),
        DashboardWindow(
            id="analytics",
            title="Analytics Window",
            status="active",
            summary="Dual-axis trend chart and NPK distribution.",
        ),
        DashboardWindow(
            id="vision",
            title="Vision Window",
            status="active",
            summary="Leaf disease detection with action-plan pipeline.",
        ),
    ]

    return DashboardOverviewResponse(
        status="success",
        generated_at=datetime.utcnow().isoformat(),
        theme="royal-violet",
        health_score=health_score,
        metrics=metrics,
        trend=_build_trend_points(readings),
        windows=windows,
    )


@router.get("/windows/{window_id}", response_model=DashboardWindowResponse)
def dashboard_window(window_id: str, db: Session = Depends(get_db)):
    trend = _build_trend_points(_latest_readings(db))

    if window_id == "overview":
        try:
            sensor_obj = SensorData(
                N=float(latest_iot_data.get("N", 88)),
                P=float(latest_iot_data.get("P", 50)),
                K=float(latest_iot_data.get("K", 42)),
                temperature=float(latest_iot_data.get("temperature", 25.5)),
                humidity=float(latest_iot_data.get("humidity", 40.0)),
                ph=float(latest_iot_data.get("ph", 6.8)),
                rainfall=float(latest_iot_data.get("rainfall", 50.0)),
                tds=float(latest_iot_data.get("tds", 150.0)),
            )
            rec_crop = predict_crop(sensor_obj)
        except Exception:
            rec_crop = "Maize"

        payload = {
            "hero": {
                "recommended_crop": rec_crop,
                "subtitle": "ML-driven recommendation powered by live real-world IoT telemetry.",
            },
            "cards": latest_iot_data,
        }
        return DashboardWindowResponse(
            status="success",
            window=window_id,
            title="Overview Window",
            payload=payload,
        )

    if window_id == "analytics":
        payload = {
            "trend_chart": [point.model_dump() for point in trend],
            "npk": {
                "N": float(latest_iot_data.get("N", 0)),
                "P": float(latest_iot_data.get("P", 0)),
                "K": float(latest_iot_data.get("K", 0)),
            },
        }
        return DashboardWindowResponse(
            status="success",
            window=window_id,
            title="Analytics Window",
            payload=payload,
        )

    if window_id == "vision":
        payload = {
            "upload": "POST /vision/disease-detect",
            "action_plan": "POST /chat/action-plan",
            "sms_alert": "POST /sms/send",
            "design_hint": "Use premium progress indicators and confidence chips.",
        }
        return DashboardWindowResponse(
            status="success",
            window=window_id,
            title="Vision Window",
            payload=payload,
        )

    raise HTTPException(status_code=404, detail="Unknown dashboard window")
