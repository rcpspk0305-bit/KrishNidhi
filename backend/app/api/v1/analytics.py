from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.db_models import Device, SensorReading, Alert, PlantProfile, PumpEvent
from app.schemas.plant_monitor_schemas import (
    AnalyticsResponse,
    AnalyticsMetrics,
    RecommendationResponse,
)
from app.analytics.rule_engine import PlantHealthEngine, calculate_vpd
from app.analytics.forecast import forecast_moisture
from app.analytics.llm_advisor import generate_natural_language_summary

router = APIRouter(prefix="/devices", tags=["Analytics & AI"])

@router.get("/{device_id}/analytics", response_model=AnalyticsResponse)
def get_device_analytics(
    device_id: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Computes statistical and physiological analytics over the specified timeframe
    including average microclimate parameters, Vapor Pressure Deficit (VPD),
    watering event counts, and soil moisture dry-down kinetics.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id, SensorReading.timestamp >= cutoff)
        .order_by(SensorReading.timestamp.desc())
        .all()
    )

    if not readings:
        return AnalyticsResponse(
            device_id=device_id,
            window_hours=hours,
            metrics=AnalyticsMetrics(),
            status_summary="No sensor telemetry recorded in the selected time window.",
        )

    temps = [r.temperature for r in readings if r.temperature is not None]
    humids = [r.humidity for r in readings if r.humidity is not None]
    soils = [r.soil_moisture for r in readings if r.soil_moisture is not None]

    avg_temp = round(sum(temps) / len(temps), 1) if temps else None
    min_temp = round(min(temps), 1) if temps else None
    max_temp = round(max(temps), 1) if temps else None

    avg_humid = round(sum(humids) / len(humids), 1) if humids else None
    avg_soil = round(sum(soils) / len(soils), 1) if soils else None
    min_soil = round(min(soils), 1) if soils else None

    # Current VPD based on latest reading
    latest = readings[0]
    current_vpd = (
        calculate_vpd(latest.temperature, latest.humidity)
        if latest.temperature is not None and latest.humidity is not None
        else None
    )

    # Watering cycles count in last 24h
    pump_events = (
        db.query(PumpEvent)
        .filter(
            PumpEvent.device_id == device_id,
            PumpEvent.timestamp >= cutoff,
            PumpEvent.confirmed_state == True,
        )
        .count()
    )

    profile = db.query(PlantProfile).filter(PlantProfile.device_id == device_id).first()
    forecast = forecast_moisture(readings, profile.preferred_moisture_min if profile else 30)
    dry_rate = forecast['dry_down_rate_pct_per_hr']

    metrics = AnalyticsMetrics(
        avg_temperature=avg_temp,
        min_temperature=min_temp,
        max_temperature=max_temp,
        avg_humidity=avg_humid,
        avg_soil_moisture=avg_soil,
        min_soil_moisture=min_soil,
        current_vpd_kpa=current_vpd,
        watering_count_24h=pump_events,
        dry_down_rate_pct_per_hr=dry_rate,
    )

    summary = (
        f"Plant microclimate is tracking an average temperature of {avg_temp or 'N/A'}°C "
        f"and soil moisture of {avg_soil or 'N/A'}% over the last {hours} hours."
    )

    return AnalyticsResponse(
        device_id=device_id,
        window_hours=hours,
        metrics=metrics,
        status_summary=summary,
        forecast=forecast,
    )

@router.get("/{device_id}/recommendations", response_model=RecommendationResponse)
def get_plant_recommendations(device_id: str, db: Session = Depends(get_db), language: str = Query("en", pattern="^(en|te|hi)$")):
    """
    Evaluates plant environmental suitability using rule-based agronomy
    and optional LLM contextual explanation.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    profile = db.query(PlantProfile).filter(PlantProfile.device_id == device_id).first()
    if not profile:
        profile = PlantProfile(
            device_id=device_id,
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
        db.refresh(profile)

    latest = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )

    history = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id,
                SensorReading.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24))
        .order_by(desc(SensorReading.timestamp))
        .all()
    )

    active_alerts = (
        db.query(Alert)
        .filter(Alert.device_id == device_id, Alert.acknowledged == False)
        .all()
    )

    # 1. Deterministic Rule-Based Assessment
    evaluation = PlantHealthEngine.evaluate(profile, latest, history, active_alerts)

    # 2. Optional Natural Language Explanation
    latest_metrics = {
        "temperature": latest.temperature if latest else None,
        "humidity": latest.humidity if latest else None,
        "soil_moisture": latest.soil_moisture if latest else None,
        "current_vpd_kpa": calculate_vpd(latest.temperature, latest.humidity)
        if latest and latest.temperature is not None and latest.humidity is not None else None,
    }
    ai_summary = generate_natural_language_summary(
        profile.plant_name, evaluation, latest_metrics, language=language
    )

    return RecommendationResponse(
        forecast=forecast_moisture(history, profile.preferred_moisture_min),
        language=language,
        device_id=device_id,
        plant_name=profile.plant_name,
        health_score=evaluation["health_score"],
        status=evaluation["status"],
        health_status=evaluation.get("health_status", evaluation["status"]),
        severity=evaluation["severity"],
        reason=evaluation.get("reason"),
        recommendation=evaluation.get("recommendation"),
        environmental_condition=evaluation.get("environmental_condition"),
        moisture_assessment=evaluation.get("moisture_assessment"),
        temperature_assessment=evaluation.get("temperature_assessment"),
        humidity_assessment=evaluation.get("humidity_assessment"),
        recommended_actions=evaluation.get("recommended_actions"),
        observations=evaluation["observations"],
        recommendations=evaluation["recommendations"],
        ai_explanation=ai_summary,
        confidence=evaluation["confidence"],
        limitations=evaluation["limitations"],
    )
