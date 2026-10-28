# System Architecture & Technical Specification

**Project:** AI-Powered IoT Smart Plant Monitoring and Automated Irrigation System  
**Hardware:** ESP8266 NodeMCU ESP-12E  
**Backend:** FastAPI & SQLAlchemy (Python 3.14 / 3.12+)  
**Frontend:** Next.js 16 (React 19, TypeScript, Tailwind CSS, Recharts)  
**Real-Time Channel:** Server-Sent Events (SSE) & HTTP Polling

---

## 1. High-Level Architectural Diagram

```text
       PHYSICAL SENSORS
    ┌──────────────────────┐
    │ DHT11 (Temp/Hum) D6  │
    │ Soil Moisture AO A0  │
    │ PIR Motion Sensor D7 │
    │ Push Button       D0 │
    └──────────┬───────────┘
               │
               ▼
     ┌────────────────────────────────────────────────────────┐
     │                ESP8266 NodeMCU ESP-12E                 │
     │  - Authoritative physical pump controller              │
     │  - 10-sample ADC moving average + calibration map      │
     │  - 15s Continuous runtime watchdog & 60s cooldown      │
     │  - 16x2 I2C LCD (4 rotating status screens)            │
     │  - Failsafe offline autonomous irrigation              │
     └──────────┬───────────────────────────────┬─────────────┘
                │                               │
                ▼                               ▼
       ┌─────────────────┐             ┌─────────────────┐
       │ 16x2 I2C LCD    │             │ 5V Relay & Pump │
       │ D2 (SDA)/D1(SCL)│             │ Pin D5 (Active-L│
       └─────────────────┘             └─────────────────┘
                │
                │ Wi-Fi (HTTP REST + JSON)
                │ (Header: X-Device-Key)
                ▼
     ┌────────────────────────────────────────────────────────┐
     │                     FastAPI Server                     │
     │  - Device Provisioning & API Key Security              │
     │  - Telemetry Ingestion & Real-time Validation          │
     │  - TTL-based Command Queue & ACK Reconciliation        │
     │  - Threshold Alert Trigger (Moisture <30%, Temp >32°C) │
     │  - Agronomic Rule Engine & VPD Transpiration Calc      │
     │  - Server-Sent Events (SSE) Broadcaster                │
     └──────────┬───────────────────────────────┬─────────────┘
                │                               │
                ▼                               ▼
       ┌─────────────────┐             ┌─────────────────┐
       │ SQLite / Postgres│            │ Gemini LLM AI   │
       │ SQLAlchemy ORM  │             │ (Advisory Only) │
       └─────────────────┘             └─────────────────┘
                │
                │ Server-Sent Events (SSE) / REST
                ▼
     ┌────────────────────────────────────────────────────────┐
     │                  Next.js Web Dashboard                 │
     │  - Real-time Health Index (0-100)                      │
     │  - Microclimate Telemetry Cards (Temp, Hum, Soil, PIR) │
     │  - Water Pump Mode Switcher (AUTO / MANUAL / OFF)      │
     │  - Confirmed vs Requested State Indicator              │
     │  - Recharts Historical Multi-Line Trend Visualization  │
     │  - Built-in Virtual ESP8266 Hardware Simulator         │
     └────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

### 2.1 Authoritative Hardware Controller
The ESP8266 NodeMCU microcontroller is the **authoritative physical controller** of the water pump relay.
- While the backend server can dispatch actuation requests (`SET_PUMP: true/false`), the ESP8266 firmware independently enforces hardware protection limits:
  1. **Maximum Continuous Runtime**: 15 seconds max continuous run.
  2. **Minimum Cooldown**: 60 seconds minimum rest between watering events to prevent soil flooding and water pooling.
  3. **Sensor Fault Lockout**: If the soil sensor reads out-of-range (<30 or >1020 ADC) or is disconnected, the pump is unconditionally forced OFF.
  4. **Relay Boot Polarity Safeguard**: Set relay pin to inactive state *before* GPIO pin configuration to eliminate boot-up clicking.
- If the Wi-Fi connection drops or the server is unreachable, the ESP8266 continues automatic irrigation based on calibrated soil moisture thresholds without interruption.

### 2.2 Distinguishing Requested vs Confirmed State
To prevent race conditions between local push-button presses and web commands:
- When a user toggles the pump on the web dashboard, the server generates a unique command ID (`cmd_xxxx`) with an expiration timestamp and status `PENDING`.
- The dashboard displays a **Pending Command** state.
- The ESP8266 retrieves the command during its 2-second polling cycle, performs physical safety verification, switches the relay, and submits an acknowledgment (`POST /ack`) reporting `status: "APPLIED"`, `confirmed_state: true/false`.
- The backend updates the database and broadcasts the confirmed state via Server-Sent Events (SSE).
- The dashboard switch snaps to the confirmed physical state.

---

## 3. Communication Sequence Diagrams

### 3.1 Real-Time Telemetry Transmission
```text
ESP8266                       FastAPI Backend                     Next.js Dashboard
   │                                 │                                   │
   │ 1. Read DHT11, A0 ADC, PIR      │                                   │
   │ 2. POST /telemetry (JSON)       │                                   │
   ├────────────────────────────────>│                                   │
   │    Header: X-Device-Key         │ 3. Validate sensor bounds         │
   │                                 │ 4. Persist to DB                  │
   │                                 │ 5. Evaluate Threshold Alerts      │
   │<────────────────────────────────┤                                   │
   │    HTTP 201 Created             │ 6. Broadcast SSE Event: telemetry │
   │                                 ├──────────────────────────────────>│
   │                                 │    Payload: Temp, Hum, Soil, PIR  │
   │                                 │                                   │ 7. Real-time UI updates
```

### 3.2 Remote Web Pump Command & Physical Acknowledgment
```text
Next.js Dashboard             FastAPI Backend                         ESP8266
   │                                 │                                   │
   │ 1. User clicks "Turn ON"        │                                   │
   │    POST /devices/{id}/pump      │                                   │
   ├────────────────────────────────>│                                   │
   │    action: "SET_PUMP", val: true│ 2. Create Command (ID: cmd_01)    │
   │<────────────────────────────────┤    Status: PENDING                │
   │    Returns cmd_01 (PENDING)     │                                   │
   │                                 │ 3. GET /commands (Poll cycle)     │
   │                                 │<──────────────────────────────────┤
   │                                 │    Header: X-Device-Key           │
   │                                 ├──────────────────────────────────>│
   │                                 │    Returns cmd_01 (SET_PUMP: true)│
   │                                 │                                   │ 4. Safety checks pass
   │                                 │                                   │ 5. Relay D5 Energized
   │                                 │ 6. POST /commands/cmd_01/ack      │
   │                                 │<──────────────────────────────────┤
   │                                 │    status: APPLIED, confirmed: true
   │                                 │ 7. Update DB & Device state       │
   │                                 │ 8. Broadcast SSE: pump_state      │
   │<────────────────────────────────┼───────────────────────────────────┤
   │    SSE: confirmed_state: true   │                                   │
   │ 9. UI switch snaps to ON        │                                   │
```

### 3.3 Physical Push-Button Actuation
```text
Push Button (D0)              ESP8266                         FastAPI Backend             Next.js Dashboard
   │                             │                                   │                           │
   │ 1. Button Pressed           │                                   │                           │
   ├────────────────────────────>│ 2. Debounce (25ms)                │                           │
   │                             │ 3. In MANUAL mode: toggle relay   │                           │
   │                             │ 4. Relay D5 transitions           │                           │
   │                             │ 5. POST /telemetry                │                           │
   │                             ├──────────────────────────────────>│                           │
   │                             │    pump_on: true, mode: "MANUAL"  │                           │
   │                             │                                   │ 6. Broadcast SSE event    │
   │                             │                                   ├──────────────────────────>│
   │                             │                                   │    pump_on: true          │
   │                             │                                   │                           │ 7. UI updates
```

---

## 4. Database Schema Relationships

```text
  +------------------+         1:N         +-----------------------+
  |     devices      |-------------------->|    sensor_readings    |
  +------------------+                     +-----------------------+
  | id (PK)          |                     | id (PK)               |
  | name             |                     | device_id (FK)        |
  | api_key_hash     |                     | temperature           |
  | status           |                     | humidity              |
  | control_mode     |                     | soil_moisture         |
  | pump_state       |                     | soil_raw              |
  | last_seen        |                     | motion_detected       |
  | created_at       |                     | pump_on               |
  +------------------+                     | timestamp             |
       |        |                          +-----------------------+
       | 1:1    | 1:N
       |        +------------------------->+-----------------------+
       |                                   |       commands        |
       v                                   +-----------------------+
  +-----------------------+                | id (PK)               |
  |    plant_profiles     |                | device_id (FK)        |
  +-----------------------+                | action                |
  | id (PK)               |                | value                 |
  | device_id (FK, Unique)|                | status (PENDING/ACK)  |
  | plant_name            |                | expires_at            |
  | preferred_temp_min/max|                +-----------------------+
  | preferred_moist_min/max|
  +-----------------------+
```
