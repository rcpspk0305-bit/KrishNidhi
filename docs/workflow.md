# Operational & Developer Workflows

This document outlines the operational and developer workflows across the Smart Plant Monitoring and KrishiNidhi AgriTech platforms.

---

## 1. Developer Daily Workflow

```text
  +------------------+       +-------------------+       +--------------------+
  | 1. Code Changes  | ----> | 2. Run Test Suite | ----> | 3. Local Run & Ver.|
  | (Firmware/Py/TS) |       |  (pytest backend) |       | (FastAPI/Streamlit)|
  +------------------+       +-------------------+       +--------------------+
```

### 1.1 Running Tests
All backend APIs, agronomic rules, and Streamlit workflows are covered by automated tests in `backend/tests/`:
```bash
pytest backend/tests -v
```

### 1.2 Running Services Locally
1. **Backend Server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. **Next.js Dashboard**:
   ```bash
   cd frontend
   npm run dev
   ```
3. **Streamlit Multi-Workspace App**:
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

---

## 2. Hardware-to-Cloud Telemetry Ingestion Workflow

1. **Non-Blocking Sensing**:
   - The ESP8266 takes periodic samples from DHT11 (temperature, humidity), soil moisture sensor (10-sample ADC moving average), and PIR motion sensor.
2. **HTTP Transmission**:
   - The device formats an HTTP POST payload with telemetry and includes the `X-Device-Key` header.
3. **Server Ingestion & Alerts**:
   - FastAPI parses the payload, validates sensor boundaries, writes to `sensor_readings`, updates device status, checks threshold alert conditions, and pushes the event to the Server-Sent Events (SSE) broadcaster.
4. **Dashboard Reflection**:
   - Web clients connected to `/api/v1/events/stream` receive sub-second updates and render the new telemetry without page refreshes.

---

## 3. Remote Actuation & Physical Reconciliation Workflow

1. **User Action**: Operator toggles pump on Next.js or via API.
2. **Command Dispatch**: Backend places a `SET_PUMP` command in the queue with a 60-second TTL (`status="PENDING"`).
3. **Hardware Poll**: ESP8266 queries `GET /api/devices/{id}/commands` every 2 seconds.
4. **Safety Check**: Microcontroller validates that continuous run limit (<15s) and cooldown (>60s) allow actuation.
5. **Relay Trigger**: Microcontroller asserts pin D5 (Active-LOW).
6. **Physical ACK**: Microcontroller posts `POST /api/devices/{id}/ack` reporting `status="APPLIED", confirmed_state=true`.
7. **SSE State Sync**: Backend persists `PumpEvent`, sets device state, and broadcasts confirmed state to all connected web clients.

For detailed architecture, see [codebase-overview.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/codebase-overview.md).
