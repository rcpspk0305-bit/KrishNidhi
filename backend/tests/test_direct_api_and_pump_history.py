import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_direct_api_telemetry_and_commands():
    device_id = "test-direct-esp8266"
    headers = {"X-Device-Key": "default_secret_key_123"}

    # 1. Test POST /api/devices/{device_id}/telemetry (direct route matching Section 5)
    telemetry_payload = {
        "temperature": 27.8,
        "humidity": 62.0,
        "soil_moisture": 45.0,
        "soil_raw": 620,
        "motion_detected": False,
        "pump_on": False,
        "control_mode": "AUTO",
    }
    res_telem = client.post(f"/api/devices/{device_id}/telemetry", json=telemetry_payload, headers=headers)
    assert res_telem.status_code == 201
    telem_data = res_telem.json()
    assert telem_data["temperature"] == 27.8
    assert telem_data["soil_moisture"] == 45.0
    assert telem_data["pump_on"] is False

    # 2. Test Poll commands before any command is queued
    res_poll1 = client.get(f"/api/devices/{device_id}/commands", headers=headers)
    assert res_poll1.status_code == 200
    poll_data1 = res_poll1.json()
    assert poll_data1["has_command"] is False
    assert poll_data1["command_id"] is None
    assert poll_data1["pump"] is None

    # 3. Post a pump command
    cmd_payload = {
        "action": "SET_PUMP",
        "value": True,
        "ttl_seconds": 60,
    }
    res_cmd = client.post(f"/api/devices/{device_id}/pump", json=cmd_payload)
    assert res_cmd.status_code == 200
    created_cmd_id = res_cmd.json()["command_id"]

    # 4. Test Poll commands via GET /api/devices/{device_id}/commands
    res_poll2 = client.get(f"/api/devices/{device_id}/commands", headers=headers)
    assert res_poll2.status_code == 200
    poll_data2 = res_poll2.json()
    assert poll_data2["has_command"] is True
    assert poll_data2["command_id"] == created_cmd_id
    assert poll_data2["pump"] is True

    # 5. Acknowledge command via POST /api/devices/{device_id}/commands/{cmd_id}/ack
    ack_payload = {
        "status": "APPLIED",
        "confirmed_state": True,
        "reason": "Relay energized physically",
    }
    res_ack = client.post(f"/api/devices/{device_id}/commands/{created_cmd_id}/ack", json=ack_payload, headers=headers)
    assert res_ack.status_code == 200
    assert res_ack.json()["confirmed_state"] is True

    # 6. Check pump history endpoint
    res_hist = client.get(f"/api/devices/{device_id}/pump/history")
    assert res_hist.status_code == 200
    hist_events = res_hist.json()
    assert len(hist_events) >= 1
    assert any(ev["confirmed_state"] is True for ev in hist_events)

    # 7. Check device status includes last_watering_time and pump_runtime_seconds
    res_status = client.get(f"/api/devices/{device_id}/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["pump_state"] is True
    assert status_data["last_watering_time"] is not None
    assert "pump_runtime_seconds" in status_data

    # 8. Check structured plant health recommendations
    res_recs = client.get(f"/api/devices/{device_id}/recommendations")
    assert res_recs.status_code == 200
    recs_data = res_recs.json()
    assert "health_status" in recs_data
    assert "reason" in recs_data
    assert "recommendation" in recs_data
    assert "environmental_condition" in recs_data
    assert "moisture_assessment" in recs_data
    assert "temperature_assessment" in recs_data
    assert "humidity_assessment" in recs_data
