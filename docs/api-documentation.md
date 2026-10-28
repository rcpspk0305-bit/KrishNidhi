# REST API Specification (API v1)

**Base URL**: `http://<server-ip>:8000/api/v1`  
**Interactive Docs**: `http://<server-ip>:8000/docs` (Swagger UI) or `/redoc`

---

## 1. Authentication Headers

- **Device Authentication**: ESP8266 requests must supply the `X-Device-Key` header:
  ```http
  X-Device-Key: <your_device_api_key>
  ```
  *(Or `Authorization: Bearer <your_device_api_key>`)*
- **User / Dashboard Authentication**: JWT token passed in standard `Authorization` header for protected administrative mutations.

---

## 2. Endpoints Summary

### 2.1 Device Management

#### `POST /api/v1/devices`
Register a new microcontroller node.
- **Request Body**:
  ```json
  {
    "id": "esp8266-plant-01",
    "name": "Indoor Greenhouse Planter",
    "api_key": "optional_custom_key_or_leave_null_to_generate"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "esp8266-plant-01",
    "name": "Indoor Greenhouse Planter",
    "status": "offline",
    "control_mode": "AUTO",
    "pump_state": false,
    "last_seen": null,
    "created_at": "2026-10-28T14:00:00Z",
    "api_key": "spk_aBcD123..."
  }
  ```

#### `GET /api/v1/devices`
List all registered devices in the system.

#### `GET /api/v1/devices/{device_id}/status`
Check real-time connectivity (online if last telemetry <= 30 seconds ago).
- **Response (200 OK)**:
  ```json
  {
    "device_id": "esp8266-plant-01",
    "status": "online",
    "online": true,
    "control_mode": "AUTO",
    "pump_state": false,
    "last_seen": "2026-10-28T14:20:00Z",
    "seconds_since_last_seen": 4.2,
    "sensor_fault": false,
    "active_alerts_count": 0
  }
  ```

---

### 2.2 Telemetry Ingestion & History

#### `POST /api/v1/devices/{device_id}/telemetry`
Called by ESP8266 every 5 seconds to submit environmental data.
- **Headers**: `X-Device-Key: <key>`
- **Request Body**:
  ```json
  {
    "temperature": 27.5,
    "humidity": 62.0,
    "soil_moisture": 42.0,
    "soil_raw": 580,
    "motion_detected": false,
    "pump_on": false,
    "control_mode": "AUTO",
    "uptime_seconds": 3600
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": 142,
    "device_id": "esp8266-plant-01",
    "timestamp": "2026-10-28T14:20:00Z",
    "temperature": 27.5,
    "humidity": 62.0,
    "soil_moisture": 42.0,
    "soil_raw": 580,
    "motion_detected": false,
    "pump_on": false,
    "control_mode": "AUTO"
  }
  ```

#### `GET /api/v1/devices/{device_id}/telemetry/latest`
Retrieve the single most recent sensor packet.

#### `GET /api/v1/devices/{device_id}/telemetry/history`
Query parameters:
- `hours`: Time window (default: 24, max: 168)
- `limit`: Max records to return (default: 50, max: 500)

---

### 2.3 Water Pump Actuator & Commands

#### `POST /api/v1/devices/{device_id}/pump`
Dispatches a pump actuation or mode switch command from the dashboard.
- **Request Body**:
  ```json
  {
    "action": "SET_PUMP",
    "value": true,
    "ttl_seconds": 60
  }
  ```
  *(Or `action: "SET_MODE"`, `value: "MANUAL"`)*
- **Response (200 OK)**:
  ```json
  {
    "command_id": "cmd_a8f9b2c3d4e5",
    "action": "SET_PUMP",
    "value": "true",
    "created_at": "2026-10-28T14:25:00Z",
    "expires_at": "2026-10-28T14:26:00Z",
    "status": "PENDING"
  }
  ```

#### `GET /api/v1/devices/{device_id}/commands`
Polled by ESP8266 every 2 seconds. Automatically expires stale commands.
- **Response (200 OK)**:
  ```json
  {
    "has_command": true,
    "command": {
      "command_id": "cmd_a8f9b2c3d4e5",
      "action": "SET_PUMP",
      "value": "true",
      "created_at": "2026-10-28T14:25:00Z",
      "expires_at": "2026-10-28T14:26:00Z",
      "status": "PENDING"
    }
  }
  ```

#### `POST /api/v1/devices/{device_id}/commands/{command_id}/ack`
Submitted by ESP8266 after executing or rejecting a command.
- **Headers**: `X-Device-Key: <key>`
- **Request Body**:
  ```json
  {
    "status": "APPLIED",
    "confirmed_state": true,
    "reason": "Relay energized successfully"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "command_id": "cmd_a8f9b2c3d4e5",
    "status": "APPLIED",
    "confirmed_state": true,
    "message": "Command cmd_a8f9b2c3d4e5 acknowledged as APPLIED"
  }
  ```

---

### 2.4 Analytics & AI Agronomy

#### `GET /api/v1/devices/{device_id}/analytics`
Computes statistical aggregates, Vapor Pressure Deficit (VPD), watering counts, and soil dry-down rate.
- **Response (200 OK)**:
  ```json
  {
    "device_id": "esp8266-plant-01",
    "window_hours": 24,
    "metrics": {
      "avg_temperature": 26.4,
      "min_temperature": 21.2,
      "max_temperature": 30.1,
      "avg_humidity": 58.2,
      "avg_soil_moisture": 46.5,
      "min_soil_moisture": 32.0,
      "current_vpd_kpa": 1.12,
      "watering_count_24h": 2,
      "total_watering_seconds_24h": 24,
      "dry_down_rate_pct_per_hr": 0.45
    },
    "status_summary": "Plant microclimate is tracking an average temperature of 26.4°C..."
  }
  ```

#### `GET /api/v1/devices/{device_id}/recommendations`
Returns agronomic health assessment and optional Gemini natural language explanation.
- **Response (200 OK)**:
  ```json
  {
    "device_id": "esp8266-plant-01",
    "plant_name": "Monstera Deliciosa",
    "health_score": 92,
    "status": "Thriving",
    "severity": "low",
    "observations": [
      "Soil moisture is optimal at 46.5% within healthy root zone bounds.",
      "Vapor Pressure Deficit is balanced at 1.12 kPa."
    ],
    "recommendations": [
      "Current environmental conditions match the profile. Continue routine monitoring."
    ],
    "ai_explanation": "Monstera Deliciosa is in peak growth condition. Continue current irrigation cadence.",
    "confidence": 0.95,
    "limitations": "Deterministic assessment based on calibrated soil moisture..."
  }
  ```

---

### 2.5 Real-Time Server-Sent Events (SSE)

#### `GET /api/v1/devices/{device_id}/events`
Long-lived HTTP streaming connection emitting real-time event updates:
- Event: `telemetry` -> Emitted immediately when sensor packet arrives.
- Event: `pump_state_updated` -> Emitted immediately when ESP8266 acks a pump state change.
- Event: `command_created` -> Emitted when remote command is enqueued.
- Event: `: keepalive heartbeat` -> Emitted every 15 seconds to keep connection alive.
