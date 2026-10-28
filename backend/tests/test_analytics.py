from app.analytics.rule_engine import calculate_vpd, PlantHealthEngine
from app.models.db_models import PlantProfile, SensorReading, Alert

def test_calculate_vpd():
    # At 25°C and 50% RH:
    # VP_sat ≈ 3.17 kPa, VPD ≈ 3.17 * 0.5 ≈ 1.58 kPa
    vpd = calculate_vpd(25.0, 50.0)
    assert 1.4 <= vpd <= 1.7

    # At 100% RH, VPD should be 0.0
    assert calculate_vpd(25.0, 100.0) == 0.0

def test_rule_engine_low_moisture_detection():
    profile = PlantProfile(
        preferred_moisture_min=30.0,
        preferred_moisture_max=65.0,
        preferred_temp_min=18.0,
        preferred_temp_max=30.0,
    )
    dry_reading = SensorReading(
        temperature=25.0,
        humidity=55.0,
        soil_moisture=15.0,
    )
    result = PlantHealthEngine.evaluate(profile, dry_reading, [], [])
    assert result["status"] == "Needs Water"
    assert result["health_score"] < 80
    assert any("critically low" in obs.lower() for obs in result["observations"])

def test_analytics_and_recommendations_api(client, seeded_device):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    # Ingest a reading
    client.post(
        f"/api/v1/devices/{dev_id}/telemetry",
        json={
            "temperature": 26.0,
            "humidity": 58.0,
            "soil_moisture": 48.0,
            "soil_raw": 530,
            "motion_detected": False,
            "pump_on": False,
            "control_mode": "AUTO",
            "uptime_seconds": 900,
        },
        headers={"X-Device-Key": api_key},
    )

    # Test analytics endpoint
    analytics_resp = client.get(f"/api/v1/devices/{dev_id}/analytics?hours=12")
    assert analytics_resp.status_code == 200
    adata = analytics_resp.json()
    assert adata["metrics"]["avg_temperature"] == 26.0
    assert adata["metrics"]["avg_soil_moisture"] == 48.0

    # Test recommendations endpoint
    rec_resp = client.get(f"/api/v1/devices/{dev_id}/recommendations")
    assert rec_resp.status_code == 200
    rdata = rec_resp.json()
    assert "health_score" in rdata
    assert "observations" in rdata
    assert "recommendations" in rdata
