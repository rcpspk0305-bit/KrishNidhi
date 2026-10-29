import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

DEVICE_TOKEN = "replace-with-a-long-random-secret"
ADMIN_TOKEN = "super_secret_admin_token_2026"


def test_health_endpoints():
    res1 = client.get("/health")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "ok"
    assert data1["database"] == "connected"

    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "ok"


def test_receive_telemetry_unauthorized():
    res = client.post(
        "/api/device/telemetry",
        json={"device_id": "plant-01", "temperature_c": 25.0, "mode": "auto"},
        headers={"X-Device-Token": "wrong-token"},
    )
    assert res.status_code == 401


def test_receive_telemetry_success():
    payload = {
        "device_id": "plant-01",
        "temperature_c": 27.5,
        "humidity_pct": 62.0,
        "soil_raw": 680,
        "soil_moisture_pct": 45.0,
        "motion": True,
        "pump_on": False,
        "mode": "auto",
    }
    res = client.post(
        "/api/device/telemetry",
        json=payload,
        headers={"X-Device-Token": DEVICE_TOKEN},
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Verify latest state reflects the telemetry
    state_res = client.get("/api/state?device_id=plant-01")
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["device_id"] == "plant-01"
    assert state["online"] is True
    assert state["telemetry"]["temperature_c"] == 27.5
    assert state["telemetry"]["humidity_pct"] == 62.0
    assert state["telemetry"]["soil_moisture_pct"] == 45.0
    assert state["telemetry"]["motion"] is True
    assert state["pump_on"] is False


def test_device_command_flow():
    # 1. Fetch initial command
    res1 = client.get(
        "/api/device/command?device_id=plant-01",
        headers={"X-Device-Token": DEVICE_TOKEN},
    )
    assert res1.status_code == 200
    initial_cmd = res1.json()
    assert "command_id" in initial_cmd
    assert "mode" in initial_cmd
    assert "pump_on" in initial_cmd

    # 2. Control pump with admin token
    control_payload = {
        "device_id": "plant-01",
        "mode": "manual",
        "pump_on": True,
    }
    res2 = client.post(
        "/api/control",
        json=control_payload,
        headers={"X-Admin-Token": ADMIN_TOKEN},
    )
    assert res2.status_code == 200
    new_cmd = res2.json()
    assert new_cmd["mode"] == "manual"
    assert new_cmd["pump_on"] is True
    assert new_cmd["command_id"] > initial_cmd["command_id"]

    # 3. Verify device receives updated command
    res3 = client.get(
        "/api/device/command?device_id=plant-01",
        headers={"X-Device-Token": DEVICE_TOKEN},
    )
    assert res3.status_code == 200
    assert res3.json()["command_id"] == new_cmd["command_id"]
    assert res3.json()["pump_on"] is True
