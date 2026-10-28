# Smart Plant Monitoring & Irrigation Dashboard - Restructuring Plan

## 1. Current Architecture
- **Frontend**: Next.js 16 (React 19, TypeScript, Tailwind CSS v4, Recharts, Lucide Icons).
  - Routes: `/` (Landing/Portal), `/dashboard` (Legacy farm overview with NPK metrics), `/login` (Simple auth), `/scheme-finder` (Farmer schemes), `/plant-monitor` (IoT Smart Plant dashboard components).
- **Backend**: FastAPI + SQLAlchemy + SQLite (`agritech.db`).
  - Routes:
    - `/api/v1/devices`: Device provisioning & status.
    - `/api/v1/telemetry`: Telemetry ingestion & historical query.
    - `/api/v1/pump`: Remote pump command queue, polling, & ACK reconciliation.
    - `/api/v1/analytics`: VPD calculation, agronomic rule engine, & LLM insights.
    - `/api/v1/events`: Server-Sent Events (SSE) live push stream.
    - Companion routes: `/predict`, `/chat`, `/sms`, `/sensors`.
- **Firmware**: ESP8266 Arduino C++ (`firmware/smart_plant/`).
  - Targeted for ESP8266 NodeMCU ESP-12E.
  - Non-blocking loop managing DHT11, A0 soil sensor, D7 PIR, D5 5V relay, D0 button, and D1/D2 16x2 I2C LCD.
- **Companion / Legacy Services**:
  - `streamlit_app.py`: Multi-tab data exploration app.
  - `iot/esp32`: Legacy ESP32 MQTT sketches.

---

## 2. Existing Features
1. **IoT Telemetry Pipeline**: Ingestion of temperature, humidity, soil moisture %, raw ADC, and PIR motion.
2. **Fail-Safe Pump Command Pipeline**: Command generation with TTL expiration, ESP8266 polling, and physical ACK verification.
3. **Agronomic Rule Engine**: Vapor Pressure Deficit (VPD) computation, moisture stress evaluation, and plant health scoring.
4. **Real-time SSE Broadcaster**: Low-latency push to web clients upon telemetry ingestion or pump ACK.
5. **Hardware Failsafes**: 15-second continuous runtime limit, 60-second cooldown, safe boot polarity, and sensor fault lockouts on firmware.

---

## 3. Features to Preserve
- **Database & Data Integrity**: SQLite schema with `SensorReading`, `Device`, `PumpEvent`, `DeviceCommand`, `Alert`, and `PlantProfile`. No destructive migrations.
- **GPIO Pinout Map**:
  - `D0` → Physical Push Button
  - `D1` → LCD SCL
  - `D2` → LCD SDA
  - `D5` → 5V Relay IN (active LOW)
  - `D6` → DHT11 DATA
  - `D7` → PIR Motion OUT
  - `A0` → Soil Moisture AO
- **Microcontroller Autonomy**: Safe local offline operation without internet or server connectivity.
- **Automated Test Suite**: Existing 19 pytest test cases in `backend/tests/`.
- **Existing Dependencies**: Retain Next.js 16, Recharts, FastAPI, and SQLAlchemy.

---

## 4. Features to Modify
1. **Dashboard Unification (`frontend/src/app/dashboard/page.tsx`)**:
   - Replace the legacy NPK field overview on `/dashboard` with the personal **AI-Powered Smart Plant Monitoring and Irrigation Dashboard**.
   - Implement the exact layout specified in Section 4:
     - **Top Section**: Plant name, Plant health status, ESP8266 connection status, Last sensor update, Current irrigation mode.
     - **Sensor Monitoring (4 Cards)**: Temperature, Humidity, Soil moisture, Motion detection.
     - **Pump Control**: Pump ON/OFF switch, AUTO/MANUAL/OFF modes, Last watering time, Pump runtime, Command confirmation status.
     - **Plant Health**: Current environmental condition, Moisture assessment, Temperature assessment, Humidity assessment, Recommended actions.
     - **Analytics**: Temperature history, Humidity history, Soil moisture history, Pump usage history (Recharts).
2. **API Endpoint Uniformity (`backend/app/main.py`)**:
   - Direct mounting of `/api/devices/{device_id}/telemetry` and `/api/devices/{device_id}/commands` in addition to `/api/v1/devices/...` to match the exact HTTP interface in Section 5.
   - Command response format normalization to include direct `{"command_id": "...", "pump": bool, "mode": "..."}` payload.
3. **Firmware Push Button Synchronization (`firmware/smart_plant/`)**:
   - Immediate telemetry dispatch flag upon local button toggle so web dashboard updates within milliseconds rather than waiting for next periodic tick.
4. **Navigation & Home Portal (`frontend/src/app/page.tsx`, `Navbar.tsx`)**:
   - Make the Smart Plant Dashboard the default focal experience. Keep secondary agricultural tools accessible in a companion menu.

---

## 5. Features to Remove / Deprecate
- Remove mock NPK data dependencies from active dashboard views.
- Disallow any AI model or LLM from triggering pump actuation directly (firmware and backend enforced).
- Remove multi-tenant / SaaS enterprise assumptions; simplify into a single-user private IoT dashboard.

---

## 6. Missing Functionality to Implement
1. **Dual-Route API Support**: Mount `/api/devices/{device_id}/...` directly for simplified ESP8266 HTTP communication.
2. **Pump Usage History & Runtime Analytics**: Track pump activations and durations for visualization in Recharts.
3. **Structured Plant Health Assessment API**: Provide granular environmental condition, moisture assessment, temperature assessment, humidity assessment, and recommended action cards.
4. **Interactive Device Irrigation Configuration**: Allow configuring minimum/maximum soil moisture thresholds and mode via the dashboard.

---

## 7. Proposed Architecture
```text
┌────────────────────────────────────────────────────────┐
│            ESP8266 NodeMCU (Firmware C++)              │
│  - DHT11 (D6), Soil AO (A0), PIR (D7), Button (D0)     │
│  - 16x2 LCD (D1/D2), 5V Relay (D5)                     │
│  - 15s Max Run Watchdog & 60s Rest Cooldown            │
│  - Autonomous Fail-Safe Logic (Runs without Wi-Fi)     │
└───────────┬────────────────────────────────┬───────────┘
            │ POST /api/devices/.../telemetry│
            │ GET  /api/devices/.../commands │
            │ POST /api/devices/.../ack      │
            ▼                                ▼
┌────────────────────────────────────────────────────────┐
│               FastAPI Personal IoT Server              │
│  - /api/devices/... & /api/v1/devices/...              │
│  - SQLite Database (`agritech.db`)                     │
│  - Command Queue with 60s Expiration                   │
│  - Agronomic Rule Engine (VPD & Health Assessments)    │
│  - Server-Sent Events (SSE) Broadcast Stream           │
└───────────┬────────────────────────────────────────────┘
            │ SSE Stream & REST API
            ▼
┌────────────────────────────────────────────────────────┐
│          Next.js Personal Web Dashboard                │
│  - Top Bar: Plant, Health, Link Status, Mode           │
│  - 4 Real-time Sensor Cards (Temp, Hum, Soil, PIR)     │
│  - Pump Control Panel (Auto/Manual/Off, Timer, Ack)    │
│  - Plant Health & Diagnostic Insights                  │
│  - Historical Trends (Temp, Hum, Soil, Pump History)   │
│  - Local Hardware Simulator Panel (Testing/Demo)       │
└────────────────────────────────────────────────────────┘
```

---

## 8. Implementation Sequence
- [x] **Phase 1: Existing Codebase Audit & Baseline Verification**:
  - Run full test suite and frontend build; audit all existing routes, models, and firmware.
- [x] **Phase 2: Dashboard Restructuring**:
  - Transformed `/dashboard` (`frontend/src/app/dashboard/page.tsx`) to the primary AI-Powered Smart Plant Monitoring and Irrigation Dashboard with the 5 required sections: Top Status, 4 Sensor Cards, Pump Control, Plant Health, and Historical Analytics.
  - Updated `frontend/src/app/page.tsx` with primary CTA pointing to `/dashboard`.
- [x] **Phase 3: ESP8266 API Integration & Dual Routing**:
  - Mounted `/api/devices/...` directly in FastAPI alongside `/api/v1/devices/...` for seamless compatibility.
  - Normalized command polling response to return `command_id`, `pump`, and `mode` at top-level.
- [x] **Phase 4: Real-time Sensor Monitoring & Plant Health**:
  - Enhanced `PlantHealthEngine` to provide distinct environmental condition, moisture assessment, temperature assessment, humidity assessment, and recommended action cards.
  - Connected live SSE push stream to dynamically update dashboard sensor cards on arrival.
- [x] **Phase 5: Pump Control & Synchronization**:
  - Implemented immediate telemetry dispatch flag upon local push button press on D0 in firmware (`pump_control.h` and `smart_plant.ino`).
  - Added `GET /{device_id}/pump/history` endpoint and client method to track pump activations.
  - Integrated last watering time and pump runtime calculation into device status.
- [x] **Phase 6: Historical Analytics Visualization**:
  - Added pump usage history stepped chart and filter tab in `TelemetryTrendsChart.tsx`.
- [x] **Phase 7: Security & Single-User Optimization**:
  - Private single-user architecture, API key authentication, and strict read-only AI isolation (AI cannot actuate relay).
- [x] **Phase 8: Comprehensive Verification & Documentation**:
  - Executed automated backend test suite: 20 passed, 0 failed in 21.78s.
  - Executed frontend production build: Next.js Turbopack completed with 0 errors.
  - Documented physical hardware verification procedures and API specifications.
