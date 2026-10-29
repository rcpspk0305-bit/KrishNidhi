---
title: "KrishiNidhi & Smart Plant Monitor Subsystems Architecture"
date: "2026-10-28"
category: "architecture-patterns"
module: "architecture"
problem_type: "architecture_pattern"
component: "infrastructure"
severity: "medium"
applies_when:
  - "Designing or modifying workflows spanning the ESP8266 IoT hardware, FastAPI backend, Next.js dashboard, or Streamlit ML portal"
  - "Extending API endpoints or implementing new real-time telemetry pipelines"
  - "Adding hardware safety constraints or sensor calibration logic"
tags:
  - "codebase-overview"
  - "iot-architecture"
  - "fastapi-backend"
  - "esp8266-firmware"
  - "nextjs-dashboard"
  - "streamlit-portal"
---

# KrishiNidhi & Smart Plant Monitor Subsystems Architecture

## Context
The NRCM-Codestrom repository contains a multi-tier IoT and AgriTech system that combines physical edge hardware (ESP8266 NodeMCU ESP-12E), a high-concurrency asynchronous API server (FastAPI + SQLite/Postgres), a responsive real-time web portal (Next.js 16 + React 19), and a data science/operational machine learning app (Streamlit).

Because the repository bridges embedded C++ firmware with web frameworks and Python data science tools, developers need a structured architecture reference explaining subsystem boundaries, data flow invariants, hardware safety guarantees, and state synchronization mechanics.

## Guidance

### 1. Architectural Boundaries & Responsibility Separation
- **Edge Microcontroller (`firmware/smart_plant/`)**: The ESP8266 is the **authoritative physical master** over the relay. The cloud backend does not directly energize actuators; instead, it enqueues commands that the edge device verifies against local safety limits (15s continuous runtime watchdog, 60s cooldown, sensor disconnect checks).
- **Backend API Server (`backend/app/`)**: Provides dual-route mounting:
  - `/api/v1/...` for typed Next.js and administrative interactions.
  - `/api/devices/...` for direct microcontroller HTTP operations (`/telemetry`, `/commands`, `/ack`).
  - Evaluates threshold alerts (e.g., soil moisture < 30%), calculates Vapor Pressure Deficit (VPD), and broadcasts real-time updates via Server-Sent Events (SSE).
- **Frontend Dashboard (`frontend/`)**: Renders real-time microclimate metrics, displays pending vs confirmed actuation states, and includes an embedded virtual ESP8266 simulator for hardware-free demonstration.
- **Operations Portal (`streamlit_app.py`)**: Dedicated multi-tab workspace for live IoT monitoring, soil-specific crop recommendation, leaf disease classification, and multilingual AI agronomist chat.

### 2. State Reconciliation Pattern
To guarantee consistency across physical hardware and remote web dashboards:
1. Web mutations create a transient `DeviceCommand` with a 60-second time-to-live (`status="PENDING"`).
2. The UI renders an unconfirmed pending state.
3. The microcontroller polls the queue during its 2-second cycle, evaluates safety limits, actuates the relay, and posts an acknowledgment (`POST /ack`).
4. The server marks the command `APPLIED`, records a `PumpEvent`, and broadcasts the confirmed state over SSE (`/api/v1/events/stream`), snapping the web switch to confirmed active.

## Why This Matters
- **Hardware Protection**: Prevents water pump burnout, soil over-saturation, and electrical hazards caused by web latency or severed network connections.
- **Operator Transparency**: Prevents user confusion by explicitly distinguishing requested actuation intent from confirmed physical relay closure.
- **Developer Predictability**: Ensures that backend services, Streamlit tools, and frontend dashboards share the same underlying database models and telemetry schemas.

## When to Apply
- When developing new actuators or sensors on the microcontroller.
- When creating or modifying API endpoints consumed by IoT hardware.
- When adding machine learning models or agronomic analytics rules.
- When onboarding new engineers to the repository.

## Examples

### Dual-Route Backend Telemetry Ingestion
```python
# Direct endpoint for ESP8266 compatibility (backend/app/api/v1/telemetry.py)
@router.post("/devices/{device_id}/telemetry", response_model=TelemetryResponse, status_code=201)
def ingest_device_telemetry(
    device_id: str,
    payload: TelemetryCreate,
    db: Session = Depends(get_db),
    x_device_key: Optional[str] = Header(None, alias="X-Device-Key")
):
    device = verify_device_credentials(device_id, x_device_key, db)
    reading = persist_telemetry(db, device, payload)
    check_threshold_alerts(db, device, payload)
    broadcast_sse("telemetry", payload.dict(), device_id)
    return reading
```

### Microcontroller Safety Loop
```cpp
// Edge hardware failsafe (firmware/smart_plant/pump_control.h)
if (pumpActive) {
    if (millis() - pumpStartTime > MAX_PUMP_RUNTIME_MS) { // 15 seconds max
        setPumpHardware(false);
        pumpActive = false;
        lastPumpStopTime = millis(); // Trigger 60s cooldown
    }
}
```

## Related
- System Overview: [docs/codebase-overview.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/codebase-overview.md)
- Architecture Guide: [docs/architecture.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/architecture.md)
- API Specification: [docs/api-documentation.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/api-documentation.md)
- Domain Concepts: [CONCEPTS.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/CONCEPTS.md)
