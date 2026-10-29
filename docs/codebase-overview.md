# KrishiNidhi & Smart Plant Monitor — Complete Codebase Architecture & System Guide

**Project:** AI-Powered IoT Smart Plant Monitoring, Automated Irrigation & AgriTech Operations Portal  
**Microcontroller:** ESP8266 NodeMCU ESP-12E (C++ Arduino Firmware)  
**Backend:** FastAPI, SQLAlchemy, Pydantic v2, Python 3.12+ (`backend/`)  
**Web Dashboard:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, Recharts (`frontend/`)  
**AI & Analytics Portal:** Streamlit Multi-Workspace App (`streamlit_app.py`)  
**Database:** SQLite (`agritech.db`) with PostgreSQL schema compatibility  
**Real-Time Transport:** Server-Sent Events (SSE) & REST Polling/ACK  
**Documentation Version:** 2.0.0 (October 2026)

---

## 1. High-Level System Architecture

This repository contains a full-stack, end-to-end agricultural IoT and machine learning ecosystem designed for real-time microclimate monitoring, autonomous irrigation with hardware-enforced fail-safes, crop suitability recommendation, and leaf disease diagnosis.

```text
                             +-------------------------------------+
                             |         PHYSICAL SENSORS            |
                             |  - DHT11 (Temp / Humidity)  (D6)    |
                             |  - Soil Moisture (Capacitive) (A0)  |
                             |  - PIR Motion Sensor         (D7)   |
                             |  - Tactile Push Button       (D0)   |
                             +------------------+------------------+
                                                |
                                                v
                             +-------------------------------------+
                             |       ESP8266 NodeMCU ESP-12E       |
                             |  - Authoritative Pump Controller    |
                             |  - 10-sample ADC Moving Average     |
                             |  - 15s Watchdog & 60s Cooldown      |
                             |  - 16x2 I2C LCD (4 Status Screens)  |
                             |  - Autonomous Offline Irrigation    |
                             +----------+----------------+---------+
                                        |                |
                          Wi-Fi REST /  |                | Active-LOW
                         X-Device-Key   |                | GPIO (D5)
                                        v                v
                     +-----------------------+     +-------------------+
                     |    FastAPI Backend    |     | 5V Relay & Pump   |
                     |  - REST Ingestion     |     +-------------------+
                     |  - Command Queue & ACK|
                     |  - Agronomic Rules    |
                     |  - SSE Broadcaster    |
                     +-----+-----------+-----+
                           |           |
            Server-Sent    |           | SQLite /
            Events (SSE)   |           | SQLAlchemy
                           v           v
           +--------------------+  +--------------------+
           | Next.js Dashboard  |  |    agritech.db     |
           | - Sensor Cards     |  | (Readings, Devices,|
           | - Pump Controller  |  |  Commands, Alerts) |
           | - Health Index Hero|  +---------+----------+
           | - Virtual Simulator|            |
           +--------------------+            |
                                             v
                             +----------------------------------+
                             |   Streamlit KrishiNidhi Portal   |
                             |  - Live IoT Stream Monitor       |
                             |  - Manual Telemetry Simulator    |
                             |  - ML Crop Recommendation Engine |
                             |  - Leaf Pathology Diagnosis      |
                             |  - Multilingual AI Agronomist    |
                             +----------------------------------+
```

---

## 2. Repository Directory Structure

```text
NRCM-Codestrom/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint, CORS, router mounts & startup
│   │   ├── api/v1/                  # Production IoT endpoints
│   │   │   ├── devices.py           # Device registration, status & plant profile management
│   │   │   ├── telemetry.py         # Telemetry ingestion, validation & threshold alert generation
│   │   │   ├── pump.py              # Command creation, device polling, ACK reconciliation & pump history
│   │   │   ├── analytics.py         # VPD calculation, agronomic health evaluation & Gemini explanations
│   │   │   ├── events.py            # Server-Sent Events (SSE) streaming endpoints
│   │   │   └── alerts.py            # Active alerts query and acknowledgment
│   │   ├── analytics/
│   │   │   ├── rule_engine.py       # Deterministic VPD and agronomic health assessment engine
│   │   │   └── llm_advisor.py       # Gemini GenAI prompt construction for agronomic explanations
│   │   ├── core/
│   │   │   ├── config.py            # Environment settings and credentials loader
│   │   │   ├── database.py          # SQLAlchemy SQLite/PostgreSQL engine and idempotent table migrations
│   │   │   └── security.py          # API key hashing (SHA-256 with salt) and JWT token handling
│   │   ├── models/
│   │   │   ├── db_models.py         # SQLAlchemy ORM models (Device, SensorReading, PumpEvent, etc.)
│   │   │   └── schemas.py           # Pydantic v2 validation models
│   │   ├── routes/                  # Companion and legacy operational endpoints
│   │   │   ├── sensors.py           # Legacy sensor ingest and historical queries
│   │   │   ├── predict.py           # ML crop prediction endpoint
│   │   │   ├── chat.py              # Agricultural chat endpoint
│   │   │   ├── sms.py               # Twilio emergency SMS alerting
│   │   │   └── dashboard.py         # Aggregated agricultural statistics
│   │   └── services/
│   │       ├── sse_service.py       # Asyncio queue-based SSE event broadcaster
│   │       ├── mqtt_service.py      # MQTT subscriber fallback for IoT gateways
│   │       ├── llm_service.py       # Google GenAI (Gemini 1.5 Flash / 2.5) client
│   │       ├── vision_service.py    # Leaf pathology classification via Gemini / heuristic fallback
│   │       └── ml_service.py        # Agronomic crop suitability classifier
│   ├── ml/
│   │   ├── crop_model.pkl           # Pretrained scikit-learn crop prediction model
│   │   ├── train.py                 # Training script for RandomForest / DecisionTree crop classifier
│   │   └── dataset/                 # Agricultural soil and climate training CSVs
│   ├── tests/                       # Comprehensive pytest suite (20 automated tests)
│   ├── requirements.txt             # Python backend dependencies
│   └── Dockerfile                   # Python FastAPI container image
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Main portal home page
│   │   │   ├── dashboard/page.tsx   # Smart Plant Monitoring and Automated Irrigation Dashboard
│   │   │   ├── plant-monitor/       # Direct route to Smart Plant Monitoring dashboard
│   │   │   ├── scheme-finder/       # Government agricultural subsidies finder
│   │   │   └── login/               # Operator authentication portal
│   │   ├── components/plant-monitor/
│   │   │   ├── PlantHealthHero.tsx      # Health score gauge, environmental status, and VPD
│   │   │   ├── SensorCardsGrid.tsx      # Temperature, Humidity, Soil %, and Motion cards
│   │   │   ├── PumpControlWidget.tsx    # Pump mode switch, manual toggle, countdown & ACK badge
│   │   │   ├── TelemetryTrendsChart.tsx # Multi-line Recharts time-series visualization
│   │   │   ├── AIRecommendationsCard.tsx# Agronomic health observations and action plans
│   │   │   ├── AlertsDrawer.tsx         # Active hardware alerts drawer
│   │   │   ├── DeviceStatusBadge.tsx    # Live device connectivity badge
│   │   │   └── HardwareSimulatorPanel.tsx # In-browser ESP8266 virtual hardware simulator
│   │   ├── hooks/
│   │   │   └── usePlantMonitorSSE.ts# React hook connecting to backend SSE events stream
│   │   ├── lib/
│   │   │   └── plantApi.ts          # Typed REST API client for backend communication
│   │   └── types/                   # TypeScript interfaces for devices, telemetry, commands, alerts
│   ├── package.json
│   └── Dockerfile                   # Next.js multi-stage container
│
├── firmware/
│   └── smart_plant/
│       ├── smart_plant.ino          # Cooperative multitasking main Arduino sketch
│       ├── config.h                 # Pinouts, Wi-Fi credentials, safety timeouts, and ADC calibration
│       ├── sensors.h                # DHT11, A0 ADC 10-sample averaging, and PIR driver
│       ├── pump_control.h           # Authoritative relay controller with watchdog & cooldown
│       ├── display.h                # 16x2 I2C LCD rotating display driver (4 screens)
│       └── network.h                # Wi-Fi auto-reconnect, JSON telemetry POST, and command poll/ACK
│
├── iot/
│   ├── esp32/                       # Companion ESP32 MQTT sketches
│   └── node-red/                    # Industrial gateway Node-RED flow definitions
│
├── docs/                            # Architectural guides, pinouts, and API specifications
├── streamlit_app.py                 # Multi-workspace KrishiNidhi Streamlit operational portal
└── docker-compose.yml               # Multi-container orchestration (FastAPI + Next.js)
```

---

## 3. Subsystem Detailed Walkthrough

### 3.1 ESP8266 Microcontroller Firmware (`firmware/smart_plant/`)

The firmware runs on an **ESP8266 NodeMCU ESP-12E** module. It operates cooperatively without blocking calls (`delay()` is forbidden in the main loop).

#### Pinout Configuration (`config.h`)
- **D6 (`GPIO 12`)**: DHT11 Temperature & Relative Humidity sensor data line.
- **A0 (`ADC 0`)**: Analog output from capacitive/resistive soil moisture sensor.
- **D7 (`GPIO 13`)**: PIR Passive Infrared Motion detector.
- **D5 (`GPIO 14`)**: 5V Relay control signal (Active-LOW optocoupled input).
- **D0 (`GPIO 16`)**: Momentary push button for local manual override (active-LOW with internal pull-up).
- **D1 (`GPIO 5`) & D2 (`GPIO 4`)**: I2C bus for 16×2 character LCD (Address `0x27`).

#### Authoritative Hardware Safety (`pump_control.h`)
The microcontroller acts as the **authoritative physical master** over the pump relay:
1. **Boot Polarity Protection**: On boot, the GPIO pin state is set HIGH (inactive) *before* `pinMode()` is invoked, preventing spurious clicks or accidental watering during microcontroller reboot.
2. **Maximum Continuous Run Watchdog**: The pump cannot run continuously for more than **15 seconds**. If this limit is reached, the state machine unconditionally forces the pump OFF.
3. **Rest Cooldown Lockout**: After any watering cycle, a mandatory **60-second cooldown period** is enforced before another actuation can occur, preventing water pooling and soil saturation.
4. **Sensor Disconnect Cutoff**: If the raw soil ADC reading is outside normal electrical bounds (<30 or >1020), a sensor fault is declared and watering is locked out.
5. **Autonomous Offline Mode**: If Wi-Fi or backend connectivity is lost, the ESP8266 continues autonomous irrigation based on calibrated soil moisture thresholds (`< 30%` triggers watering; `> 55%` stops watering).
6. **Local Push-Button Sync**: Pressing the physical tactile button toggles the pump in `MANUAL` mode and immediately flags telemetry for dispatch so the web dashboard updates within milliseconds.

---

### 3.2 FastAPI Backend Core (`backend/app/`)

The backend is built with FastAPI and runs on port `8000`.

#### Dual-Route REST Mounting (`backend/app/main.py`)
To support standard versioned web clients alongside resource-constrained IoT devices, the backend mounts both:
1. `/api/v1/...`: Standard REST API for Next.js, Streamlit, and administrative clients.
2. `/api/devices/...`: Direct shorthand endpoints matching ESP8266 firmware HTTP requests:
   - `POST /api/devices/{device_id}/telemetry`
   - `GET /api/devices/{device_id}/commands`
   - `POST /api/devices/{device_id}/ack`

#### Core API Services:
1. **Device Provisioning (`api/v1/devices.py`)**:
   - Manages device identity, security API key generation, online status detection (online if `last_seen <= 30s`), and associated `PlantProfile` parameters.
2. **Telemetry Ingestion & Alerts (`api/v1/telemetry.py`)**:
   - Validates sensor bounds, persists readings to `sensor_readings`, evaluates threshold alerts (e.g., `SOIL_DRY` if moisture < 30%, `HIGH_TEMP` if temp > 32°C), updates device `last_seen`, and broadcasts an SSE event.
3. **Command Queue & ACK Reconciliation (`api/v1/pump.py`)**:
   - Creates commands with a 60-second TTL (`PENDING` status).
   - ESP8266 retrieves pending commands during its 2-second polling cycle.
   - When the microcontroller actuates the relay, it submits an acknowledgment (`POST /ack`).
   - The server marks the command `APPLIED`, updates device `pump_state`, logs a `PumpEvent`, and broadcasts the confirmed state over SSE.
4. **Server-Sent Events Broadcaster (`services/sse_service.py`, `api/v1/events.py`)**:
   - High-performance `SSEBroadcaster` managing per-device and global client `asyncio.Queue` subscribers for real-time telemetry streaming to browsers.
5. **Agronomic Rule Engine (`analytics/rule_engine.py`)**:
   - Calculates **Vapor Pressure Deficit (VPD)** using the Tetens equation:
     $$\text{VP}_{\text{sat}} = 0.61078 \times \exp\left(\frac{17.27 \times T}{T + 237.3}\right)$$
     $$\text{VPD} = \text{VP}_{\text{sat}} \times \left(1 - \frac{\text{RH}}{100}\right)$$
   - Evaluates moisture deficit/excess, thermal stress, and transpiration rates to compute an explainable **Health Score (0–100)** with actionable recommendations.
6. **Gemini LLM Integration (`services/llm_service.py`, `analytics/llm_advisor.py`)**:
   - Connects to Google GenAI (`gemini-1.5-flash`) to generate contextual natural language recommendations and conversational agronomic advice in multiple languages (English, Hindi, Telugu).

---

### 3.3 Streamlit KrishiNidhi Operations Portal (`streamlit_app.py`)

A rich, interactive 728-line operational portal featuring a dark-violet glassmorphic UI (`#0a0512` background, purple accents `#8a2be2`). It imports backend models and services directly and serves four distinct workspaces:

1. **📊 Real-time Dashboard**:
   - **Live IoT Stream**: Displays live hardware connection state, packet counter, and telemetry values directly from the shared SQLite database.
   - **Manual Telemetry Simulator**: Allows testing telemetry by providing interactive sliders for Temperature, Humidity, Soil Moisture, pH, NPK, and TDS, with a button to push readings directly into the database.
   - **Historical Sensor Trends**: Interactive Plotly time-series charts visualizing microclimate history.
2. **🌾 Crop Recommendation**:
   - Soil-specific crop advisor using an agronomic suitability model based on soil chemistry (N, P, K, pH) and environmental telemetry (temperature, humidity, rainfall).
3. **🍃 Leaf Disease Diagnosis**:
   - Image upload module utilizing Gemini Vision (or agronomic heuristic fallback) to classify plant diseases (e.g., Early Blight, Late Blight, Leaf Curl, Powdery Mildew) with confidence metrics.
4. **🤖 KrishiNidhi AI Chatbot**:
   - Multi-turn conversation interface for farmers and operators, powered by Google GenAI.

---

### 3.4 Next.js 16 Web Dashboard (`frontend/`)

Built with React 19, Next.js 16 (App Router), TypeScript, Tailwind CSS v4, Lucide Icons, and Recharts.

#### Key Dashboard Components:
- **`PlantHealthHero`**: Displays plant name, health status badge, large 0-100 score gauge, and current VPD reading with stomatal opening indicator.
- **`SensorCardsGrid`**: 4 real-time telemetry cards (Temperature, Humidity, Soil Moisture %, and PIR Motion) with color-coded status rings and historical ranges.
- **`PumpControlWidget`**:
  - Irrigation mode toggle: `AUTO` (autonomous sensor threshold), `MANUAL` (user controlled), `OFF` (lockout).
  - Actuation switch showing **Requested State** vs **Confirmed Hardware State**.
  - Safety countdown timer showing remaining runtime or cooldown rest period.
  - Pump activation history table showing recent watering events, durations, and triggering sources.
- **`TelemetryTrendsChart`**: Synchronized Recharts multi-line chart for historical temperature, humidity, and soil moisture analysis.
- **`AIRecommendationsCard`**: Structured cards showing moisture assessment, thermal stress, and recommended agronomic actions.
- **`HardwareSimulatorPanel`**: A virtual ESP8266 controller embedded directly in the web page. Enables full end-to-end demonstrations (pushing telemetry, receiving pump commands, and acknowledging state) when physical hardware is not plugged in.

---

## 4. Database Schema Relationships (`backend/app/models/db_models.py`)

The system utilizes SQLAlchemy ORM with support for SQLite (`agritech.db`) and PostgreSQL.

```text
    +------------------------------------+
    |              devices               |
    +------------------------------------+
    | id (PK, String 64)                 |<-----+
    | name (String 128)                  |      |
    | api_key_hash (String 128)          |      |
    | status (String 32: online/offline) |      |
    | control_mode (AUTO/MANUAL/OFF)     |      |
    | pump_state (Boolean)               |      |
    | last_seen (DateTime)               |      |
    | created_at (DateTime)              |      |
    +-----------------+------------------+      |
                      | 1                       |
                      |                         |
       +--------------+--------------+          |
       | 1:N          | 1:N          | 1:1      |
       v              v              v          |
+---------------+ +------------+ +-------------+|
|sensor_readings| |  commands  | |plant_profile||
+---------------+ +------------+ +-------------+|
|id (PK)        | |id (PK)     | |id (PK)      ||
|device_id (FK) | |device_id   | |device_id(FK)||
|temperature    | |action      | |plant_name   ||
|humidity       | |value       | |pref_temp_min||
|soil_moisture  | |status      | |pref_moist_..||
|soil_raw       | |expires_at  | +-------------+|
|motion_detected| |executed_at |                |
|pump_on        | +------------+                |
|timestamp      |                               |
+---------------+                               |
       | 1:N                                    |
       v                                        |
+---------------+                               |
|  pump_events  |-------------------------------+
+---------------+
|id (PK)        |
|device_id (FK) |
|requested_state|
|confirmed_state|
|source / reason|
|timestamp      |
+---------------+
```

---

## 5. End-to-End Operational Workflows

### 5.1 Telemetry Ingestion Flow
1. ESP8266 reads sensors: DHT11 temperature/humidity, 10-sample averaged soil ADC, and PIR pin.
2. ESP8266 sends HTTP `POST /api/devices/{id}/telemetry` with `X-Device-Key` header.
3. Backend validates authentication, checks telemetry ranges, and saves record to `sensor_readings`.
4. Backend evaluates alert triggers (e.g. soil moisture < 30%) and persists alerts if triggered.
5. Backend invokes `sse_manager.broadcast("telemetry", data, device_id)`.
6. Next.js dashboard receives SSE message and updates sensor cards and trend charts without reloading.

### 5.2 Remote Web Actuation & Physical Acknowledgment Flow
1. User clicks "Turn Pump ON" on Next.js dashboard.
2. Dashboard posts `POST /api/v1/pump/command` with `{"action": "SET_PUMP", "value": "true"}`.
3. Backend generates a `DeviceCommand` with `status="PENDING"` and a 60-second expiration.
4. Dashboard shows an amber badge: `Command Pending...`.
5. ESP8266 polls `GET /api/devices/{id}/commands`.
6. Microcontroller receives command, checks local safety limits (watchdog and cooldown).
7. Microcontroller pulls GPIO D5 LOW (relay turns ON) and records start timestamp.
8. ESP8266 sends `POST /api/devices/{id}/ack` reporting `status="APPLIED", confirmed_state=true`.
9. Backend updates command to `APPLIED`, records a `PumpEvent`, and broadcasts SSE `pump_state`.
10. Dashboard switch snaps to confirmed green `PUMP ON`.

---

## 6. Automated Verification & Testing Suite (`backend/tests/`)

The repository includes a comprehensive test suite of 20 test cases in `backend/tests/`:

1. `test_devices.py`: Device registration, listing, status checking, and API key authentication.
2. `test_telemetry.py`: Telemetry packet ingestion, out-of-range sensor rejection, and automatic alert creation.
3. `test_pump_control.py`: Pump command queueing, command polling, TTL expiration, and ACK confirmation.
4. `test_direct_api_and_pump_history.py`: Direct `/api/devices/...` route compatibility and pump activation event history.
5. `test_analytics.py`: VPD mathematical calculations and agronomic health rule evaluation.
6. `test_streamlit_workflows.py`: Streamlit `AppTest` testing page boot, real-time dashboard simulator push, crop suitability engine, leaf disease diagnosis, and chatbot flow.

---

## 7. Quick Execution & Development Runbook

### Running FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- Swagger UI Documentation: `http://localhost:8000/docs`

### Running Streamlit AgriTech Portal
```bash
# Run from repository root so backend imports resolve cleanly
streamlit run streamlit_app.py --server.port 8501
```
- Streamlit Portal: `http://localhost:8501`

### Running Next.js Web Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Web Dashboard: `http://localhost:3000/dashboard` (or `http://localhost:3000/plant-monitor`)

### Running Dockerized Full-Stack
```bash
docker compose up --build -d
```
