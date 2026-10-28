def test_register_device(client):
    payload = {
        "id": "esp8266-new-node",
        "name": "Garden Planter 02",
        "api_key": "my_secret_token_12345",
    }
    response = client.post("/api/v1/devices", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "esp8266-new-node"
    assert data["name"] == "Garden Planter 02"
    assert data["api_key"] == "my_secret_token_12345"

def test_duplicate_device_registration_fails(client, seeded_device):
    dev_id = seeded_device["device"].id
    payload = {
        "id": dev_id,
        "name": "Duplicate Device",
    }
    response = client.post("/api/v1/devices", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_list_devices(client, seeded_device):
    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert any(d["id"] == seeded_device["device"].id for d in items)

def test_get_device_status(client, seeded_device):
    dev_id = seeded_device["device"].id
    response = client.get(f"/api/v1/devices/{dev_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == dev_id
    assert "online" in data
    assert "control_mode" in data

def test_update_plant_profile(client, seeded_device):
    dev_id = seeded_device["device"].id
    update_data = {
        "plant_name": "Ghost Pepper",
        "preferred_temp_max": 35.0,
        "preferred_moisture_min": 25.0,
    }
    response = client.put(f"/api/v1/devices/{dev_id}/profile", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["plant_name"] == "Ghost Pepper"
    assert data["preferred_temp_max"] == 35.0
    assert data["preferred_moisture_min"] == 25.0
