from datetime import datetime, timezone, timedelta
from app.models.db_models import DeviceCommand

def test_pump_command_flow_and_ack(client, seeded_device, db_session):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    # 1. Dashboard requests to turn pump ON
    cmd_payload = {
        "action": "SET_PUMP",
        "value": True,
        "ttl_seconds": 60,
    }
    create_resp = client.post(f"/api/v1/devices/{dev_id}/pump", json=cmd_payload)
    assert create_resp.status_code == 200
    cmd_data = create_resp.json()
    command_id = cmd_data["command_id"]
    assert cmd_data["status"] == "PENDING"
    assert cmd_data["action"] == "SET_PUMP"

    # 2. ESP8266 polls for pending commands
    poll_resp = client.get(
        f"/api/v1/devices/{dev_id}/commands",
        headers={"X-Device-Key": api_key},
    )
    assert poll_resp.status_code == 200
    poll_data = poll_resp.json()
    assert poll_data["has_command"] is True
    assert poll_data["command"]["command_id"] == command_id
    assert poll_data["command"]["action"] == "SET_PUMP"

    # 3. ESP8266 executes command, verifies relay, and submits ACK
    ack_payload = {
        "status": "APPLIED",
        "confirmed_state": True,
        "reason": "Relay contact energized successfully",
    }
    ack_resp = client.post(
        f"/api/v1/devices/{dev_id}/commands/{command_id}/ack",
        json=ack_payload,
        headers={"X-Device-Key": api_key},
    )
    assert ack_resp.status_code == 200
    ack_data = ack_resp.json()
    assert ack_data["status"] == "APPLIED"
    assert ack_data["confirmed_state"] is True

    # 4. Verify device status reflects confirmed state
    status_resp = client.get(f"/api/v1/devices/{dev_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["pump_state"] is True

def test_command_expiration(client, seeded_device, db_session):
    dev_id = seeded_device["device"].id
    api_key = seeded_device["api_key"]

    # Insert an already-expired command directly into DB
    expired_cmd = DeviceCommand(
        id="cmd_expired_test",
        device_id=dev_id,
        action="SET_PUMP",
        value="true",
        status="PENDING",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    db_session.add(expired_cmd)
    db_session.commit()

    # ESP8266 polls: expired command should be marked EXPIRED and NOT returned
    poll_resp = client.get(
        f"/api/v1/devices/{dev_id}/commands",
        headers={"X-Device-Key": api_key},
    )
    assert poll_resp.status_code == 200
    poll_data = poll_resp.json()
    assert poll_data["has_command"] is False
