def test_ingest_telemetry_success(client, seeded_device):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    payload = {
        "temperature": 27.5,
        "humidity": 62.0,
        "soil_moisture": 45.0,
        "soil_raw": 550,
        "motion_detected": False,
        "pump_on": False,
        "control_mode": "AUTO",
        "uptime_seconds": 3600,
    }

    response = client.post(
        f"/api/v1/devices/{dev_id}/telemetry",
        json=payload,
        headers={"X-Device-Key": api_key},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == dev_id
    assert data["temperature"] == 27.5
    assert data["humidity"] == 62.0
    assert data["soil_moisture"] == 45.0
    assert data["motion_detected"] is False

def test_ingest_telemetry_unauthorized(client, seeded_device):
    dev_id = seeded_device["device"].id
    payload = {
        "temperature": 25.0,
        "humidity": 55.0,
        "soil_moisture": 40.0,
        "soil_raw": 600,
        "motion_detected": False,
        "pump_on": False,
        "control_mode": "AUTO",
        "uptime_seconds": 100,
    }
    response = client.post(
        f"/api/v1/devices/{dev_id}/telemetry",
        json=payload,
        headers={"X-Device-Key": "WRONG_SECRET_KEY"},
    )
    assert response.status_code == 401

def test_low_soil_moisture_triggers_alert(client, seeded_device):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    # Soil moisture below 30% threshold
    payload = {
        "temperature": 29.0,
        "humidity": 45.0,
        "soil_moisture": 18.0,
        "soil_raw": 820,
        "motion_detected": False,
        "pump_on": False,
        "control_mode": "AUTO",
        "uptime_seconds": 1200,
    }

    response = client.post(
        f"/api/v1/devices/{dev_id}/telemetry",
        json=payload,
        headers={"X-Device-Key": api_key},
    )
    assert response.status_code == 201

    # Verify alert was generated
    alert_resp = client.get(f"/api/v1/devices/{dev_id}/alerts")
    assert alert_resp.status_code == 200
    alerts = alert_resp.json()
    assert any(a["type"] == "SOIL_DRY" for a in alerts)

def test_get_telemetry_history(client, seeded_device):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    # Ingest two readings
    for t in [25.0, 26.0]:
        client.post(
            f"/api/v1/devices/{dev_id}/telemetry",
            json={
                "temperature": t,
                "humidity": 60.0,
                "soil_moisture": 50.0,
                "soil_raw": 500,
                "motion_detected": False,
                "pump_on": False,
                "control_mode": "AUTO",
                "uptime_seconds": 200,
            },
            headers={"X-Device-Key": api_key},
        )

    response = client.get(f"/api/v1/devices/{dev_id}/telemetry/history?limit=10&hours=24")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] >= 2
