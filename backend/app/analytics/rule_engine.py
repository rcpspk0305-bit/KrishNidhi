import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.models.db_models import PlantProfile, SensorReading, Alert
from app.analytics.forecast import forecast_moisture

def calculate_vpd(temp_c: float, humidity_pct: float) -> float:
    """
    Calculates Vapor Pressure Deficit (VPD) in kiloPascals (kPa).
    VPD = VP_sat * (1 - RH / 100)
    where VP_sat = 0.61078 * exp((17.27 * T) / (T + 237.3))
    """
    if temp_c is None or humidity_pct is None:
        return 0.0
    vp_sat = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    vpd = vp_sat * (1.0 - (humidity_pct / 100.0))
    return round(max(0.0, vpd), 2)

class PlantHealthEngine:
    @staticmethod
    def evaluate(
        profile: PlantProfile,
        latest_reading: Optional[SensorReading],
        history: List[SensorReading],
        active_alerts: List[Alert],
    ) -> Dict[str, Any]:
        """
        Deterministic, rule-based agronomic evaluation engine.
        Produces explainable observations, actionable recommendations, and health score.
        """
        observations: List[str] = []
        recommendations: List[str] = []
        warnings: List[str] = []
        health_score = 100
        severity = "low"
        status = "Optimal"

        if not latest_reading:
            return {
                "health_score": 0,
                "status": "No Telemetry",
                "health_status": "Needs Attention",
                "severity": "medium",
                "reason": "No sensor telemetry received yet from the device.",
                "recommendation": "Check ESP8266 power supply and Wi-Fi connection.",
                "environmental_condition": "Awaiting Telemetry",
                "moisture_assessment": "Sensor data pending",
                "temperature_assessment": "Sensor data pending",
                "humidity_assessment": "Sensor data pending",
                "recommended_actions": ["Check ESP8266 power supply and Wi-Fi connection."],
                "observations": ["No sensor data received yet from the device."],
                "recommendations": ["Check ESP8266 power supply and Wi-Fi connection."],
                "confidence": 0.0,
                "limitations": "Awaiting first telemetry packet from physical hardware.",
            }

        temp = latest_reading.temperature
        humidity = latest_reading.humidity
        soil_moisture = latest_reading.soil_moisture
        available_sensors = sum(value is not None for value in (temp, humidity, soil_moisture))
        if available_sensors < 3:
            observations.append("Some sensor readings are missing; health assessment is incomplete.")
            recommendations.append("Check sensor wiring and wait for complete telemetry before relying on this assessment.")

        # 1. Soil Moisture Assessment
        min_moisture = profile.preferred_moisture_min or 30.0
        max_moisture = profile.preferred_moisture_max or 65.0

        if soil_moisture is not None:
            if soil_moisture < min_moisture:
                deficit = min_moisture - soil_moisture
                health_score -= min(35, int(deficit * 1.5))
                observations.append(
                    f"Soil moisture is critically low at {soil_moisture:.1f}% (target: {min_moisture:.0f}%–{max_moisture:.0f}%)."
                )
                recommendations.append(
                    "Irrigation cycle recommended. In AUTO mode, the ESP8266 will trigger safe watering."
                )
                severity = "high"
                status = "Needs Water"
            elif soil_moisture > max_moisture + 15:
                excess = soil_moisture - max_moisture
                health_score -= min(25, int(excess * 1.0))
                observations.append(
                    f"Soil is saturated at {soil_moisture:.1f}%. High risk of root hypoxia or root rot."
                )
                recommendations.append(
                    "Temporarily pause irrigation. Ensure proper drainage in the planter."
                )
                if severity != "high":
                    severity = "medium"
                    status = "Over-watered"
            else:
                observations.append(
                    f"Soil moisture is optimal at {soil_moisture:.1f}% within healthy root zone bounds."
                )

        # 2. Temperature & Heat Stress Assessment
        min_temp = profile.preferred_temp_min or 18.0
        max_temp = profile.preferred_temp_max or 30.0

        if temp is not None:
            if temp > max_temp:
                health_score -= min(20, int((temp - max_temp) * 3))
                observations.append(
                    f"Ambient temperature ({temp:.1f}°C) exceeds preferred upper threshold ({max_temp:.1f}°C)."
                )
                recommendations.append(
                    "Provide shade or increase ventilation to prevent thermal transpiration shock."
                )
                if severity == "low":
                    severity = "medium"
            elif temp < min_temp:
                health_score -= min(20, int((min_temp - temp) * 3))
                observations.append(
                    f"Ambient temperature ({temp:.1f}°C) is below minimum threshold ({min_temp:.1f}°C)."
                )
                recommendations.append(
                    "Move plant away from cold drafts or provide passive thermal insulation."
                )
                if severity == "low":
                    severity = "medium"
            else:
                observations.append(f"Temperature is stable at {temp:.1f}°C (target {min_temp:.0f}–{max_temp:.0f}°C).")

        # 3. Vapor Pressure Deficit (VPD)
        if temp is not None and humidity is not None:
            vpd = calculate_vpd(temp, humidity)
            if vpd < 0.4:
                observations.append(f"VPD is low ({vpd:.2f} kPa); high humidity limits natural transpiration.")
                recommendations.append("Increase air circulation to minimize fungal pathogen risk.")
                health_score -= 5
            elif vpd > 1.5:
                observations.append(f"VPD is elevated ({vpd:.2f} kPa); dry air causes accelerated moisture loss.")
                recommendations.append("Mist foliage or raise ambient relative humidity.")
                health_score -= 10
            else:
                observations.append(f"Vapor Pressure Deficit is balanced at {vpd:.2f} kPa.")

        # Use the same robust fit for the narrative and the forecast card.
        forecast = forecast_moisture(history, min_moisture)
        rate = forecast['dry_down_rate_pct_per_hr']
        if rate is not None and rate > 0.1:
            observations.append(f"Estimated soil dry-down rate is {rate:.2f}% moisture loss per hour.")

        # 5. Active Alerts Penalty
        for alert in active_alerts:
            if not alert.acknowledged:
                if alert.severity == "critical":
                    health_score -= 25
                    status = "Critical Alert"
                    severity = "high"
                elif alert.severity == "high":
                    health_score -= 15
                    if severity != "high":
                        severity = "medium"

        # Final score normalization
        health_score = max(0, min(100, health_score))
        if health_score >= 80 and status not in ["Needs Water", "Over-watered", "Critical Alert"] and severity == "low":
            status = "Optimal"
            severity = "low"
        elif health_score < 60 and status == "Optimal":
            status = "Needs Attention"
            severity = "medium"

        if not recommendations:
            recommendations.append("Current environmental conditions match the profile. Continue routine monitoring.")

        # Determine primary reason and primary recommendation
        primary_reason = observations[0] if observations else "Environmental parameters within nominal operating range."
        primary_rec = recommendations[0] if recommendations else "Continue autonomous monitoring."

        # Compute assessments
        env_cond = f"{temp:.1f}°C, {humidity:.0f}% RH" if temp is not None and humidity is not None else "Sensor reading in progress"
        moisture_eval = "Unavailable" if soil_moisture is None else f"{soil_moisture:.1f}% ({'below target' if soil_moisture < min_moisture else 'optimal' if soil_moisture <= max_moisture else 'above target'})"
        temp_eval = "Unavailable" if temp is None else f"{temp:.1f}°C ({'optimal' if min_temp <= temp <= max_temp else 'warm' if temp > max_temp else 'cool'})"
        humid_eval = "Unavailable" if humidity is None else f"{humidity:.0f}% RH ({'optimal' if 40 <= humidity <= 80 else 'abnormal'})"
        if available_sensors == 0:
            status, severity, health_score = "Sensor Data Missing", "medium", 0
        elif available_sensors < 3 and status == "Optimal":
            status, severity = "Incomplete Assessment", "medium"

        return {
            "health_score": health_score,
            "status": status,
            "health_status": status,
            "severity": severity,
            "reason": primary_reason,
            "recommendation": primary_rec,
            "environmental_condition": env_cond,
            "moisture_assessment": moisture_eval,
            "temperature_assessment": temp_eval,
            "humidity_assessment": humid_eval,
            "recommended_actions": recommendations,
            "observations": observations,
            "recommendations": recommendations,
            "confidence": round(available_sensors / 3, 2),
            "limitations": "Rule-based assessment, not a trained diagnosis. The confidence field reports sensor coverage, not predictive accuracy. Calibration and fresh telemetry are required; this does not replace lab soil testing.",
        }
