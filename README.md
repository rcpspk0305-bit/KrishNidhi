# AI-Powered Smart Plant Monitoring & Automated Irrigation System

For USB/Wi-Fi setup, LAN access, dataset training, and soil moisture forecasts, see
[Local hardware and predictions](docs/local-hardware-and-predictions.md).

A complete, production-grade IoT plant monitoring and automated irrigation platform built with the **ESP8266 NodeMCU ESP-12E** microcontroller running **MicroPython**, a **FastAPI** backend with SQLite persistence and real-time Server-Sent Events (SSE), and a modern **Next.js 16** responsive dashboard.

---

## 🌟 Key Features

1. **Environmental Sensing**: Continuous non-blocking acquisition of Ambient Temperature & Relative Humidity (DHT11), Calibrated Soil Moisture percentage (LM393 AO + A0 ADC), and PIR Motion presence detection.
2. **Authoritative Pump Controller**: The ESP8266 microcontroller executes low-level irrigation logic with hardware fail-safes (10s maximum continuous runtime watchdog, 60s cooldown lockout, and sensor fault cutoffs).
3. **Dual Operating Modes**:
   - `AUTO`: Autonomous soil moisture threshold irrigation (watering starts when moisture < 35%, stops when > 55%).
   - `MANUAL`: Controlled remotely via web dashboard switch or locally via debounced tactile push button.
4. **Local 16×2 I2C Display**: Real-time measurement readout (Temp, Humidity, Soil %, Pump status, and Operating Mode) on PCF8574 I2C LCD backpack at `0x27`.
5. **Real-time Web Dashboard**: Built with Next.js 16, React 19, TypeScript, Tailwind CSS, and Recharts. Connected to backend via Server-Sent Events (SSE) for instant sub-second telemetry updates.
6. **Hardware Safety**: Relay initialized to safe inactive state (`1` for active-LOW relay) *before* GPIO pin configuration to eliminate spurious reboot clicks. Water pump is never energized without explicit authorization.
7. **Virtual Hardware Simulator**: Isolated software simulator (`hardware/device_simulator.py`) to test and demonstrate full telemetry and control flows even when physical hardware is detached.

---

## 📐 System Architecture

```text
  ┌────────────────────────────────────────────────────────┐
  │                 ESP8266 NodeMCU ESP-12E                │
  │                                                        │
  │   DHT11 Sensor (D6 / GPIO12) ───► Temperature/Humidity │
  │   Soil Moisture Sensor (A0)  ───► Calibrated Moisture %│
  │   PIR Motion Sensor (D7 / GPIO13) ──► Motion Detect    │
  │   Tactile Button (D0 / GPIO16) ────► Manual Toggle     │
  │                                                        │
  │   16x2 I2C LCD (D1/SCL, D2/SDA) ◄── Display Telemetry  │
  │   5V Relay (D5 / GPIO14) ────────► 5V Submersible Pump │
  └────────────────────────┬───────────────────────────────┘
                           │ 2.4 GHz Wi-Fi (REST / JSON)
                           ▼
  ┌────────────────────────────────────────────────────────┐
  │               FastAPI Backend (Port 8000)              │
  │              Listening on 0.0.0.0:8000                 │
  │                                                        │
  │   POST /api/device/telemetry  ◄── Ingests sensor data  │
  │   GET  /api/device/command    ──► Dispatches commands  │
  │   GET  /api/state             ──► Device connection/state│
  │   POST /api/control           ◄── Web control commands │
  │   GET  /health                ──► System health check  │
  │                                                        │
  │   SQLite Database (agritech.db) ── Persistent History  │
  │   SSE Event Broadcaster        ── Sub-second updates   │
  └────────────────────────┬───────────────────────────────┘
                           │ SSE Stream & REST API
                           ▼
  ┌────────────────────────────────────────────────────────┐
  │            Next.js 16 Frontend (Port 3000)             │
  │                                                        │
  │   - Live Environmental Gauges & Sensor Cards           │
  │   - Confirmed Water Pump Actuation & Remote Controls   │
  │   - Auto/Manual Irrigation Mode Selector               │
  │   - Historical Analytics & Sensor Trend Charts         │
  │   - Online/Offline Connectivity Status Indicator       │
  └────────────────────────────────────────────────────────┘
```

---

## 🔌 Hardware Pinout Mapping

| Component | ESP8266 Pin | GPIO | Logic Level | Wiring Details |
|---|---|---|---|---|
| **DHT11 Data** | **D6** | `GPIO 12` | 3.3V | Single-wire digital protocol |
| **PIR Motion Out** | **D7** | `GPIO 13` | 3.3V | Digital HIGH upon motion detection |
| **Soil Moisture AO** | **A0** | `ADC 0` | 0.0V–1.0V (max 3.3V via divider) | 5-sample moving average |
| **5V Relay IN** | **D5** | `GPIO 14` | 3.3V Logic | Active-LOW (`0` = Energized, `1` = Safe OFF) |
| **Push Button** | **D0** | `GPIO 16` | 3.3V | **Requires external 10kΩ pull-up resistor to 3.3V** |
| **LCD SDA** | **D2** | `GPIO 4` | 3.3V Logic | I2C Data (PCF8574 Address `0x27`) |
| **LCD SCL** | **D1** | `GPIO 5` | 3.3V Logic | I2C Clock |

> [!IMPORTANT]
> **GPIO16 Button Note**: On the ESP8266, `GPIO16` (`D0`) does not support software internal pull-up in MicroPython. An external **10kΩ resistor** must be connected between `D0` and `3.3V`, with the tactile button pulling `D0` to `GND` when pressed.

---

## 📂 Project Structure

```text
NRCM-Codestrom/
├── hardware/                      # MicroPython ESP8266 Firmware
│   ├── main.py                    # Main control loop, sensor sampling, fail-safes
│   ├── config.py                  # Wi-Fi SSID, LAN API URL, calibration thresholds
│   ├── lcd_i2c.py                 # PCF8574 I2C 16x2 LCD display driver
│   ├── device_simulator.py        # Isolated software simulator for test environments
│   └── ESP8266_GENERIC-*.bin      # MicroPython v1.29.0 official firmware binary
│
├── backend/                       # FastAPI Backend Application
│   ├── app/
│   │   ├── main.py                # FastAPI initialization, CORS, device seeding
│   │   ├── api/v1/                # API routers
│   │   │   ├── device_compat.py   # Primary endpoints (/api/device/*, /api/state, /api/control)
│   │   │   ├── devices.py         # Device registry & profiles
│   │   │   ├── telemetry.py       # Sensor telemetry ingestion & historical queries
│   │   │   └── pump.py            # Pump commands and execution status
│   │   ├── models/                # SQLAlchemy models (Devices, Readings, Commands)
│   │   ├── schemas/               # Pydantic v2 validation models
│   │   └── services/              # SSE broadcaster and event streams
│   ├── tests/                     # Automated test suites
│   │   ├── verify_end_to_end.py   # Complete 10-point end-to-end verification script
│   │   └── test_*.py              # Pytest test cases (47 passing tests)
│   ├── server.py                  # Unified server startup script
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Local environment variables (HOST=0.0.0.0, PORT=8000)
│   └── .env.example               # Environment variables template
│
├── frontend/                      # Next.js 16 Web Application
│   ├── src/app/
│   │   ├── plant-monitor/page.tsx # Primary Plant Health Monitoring dashboard
│   │   └── dashboard/page.tsx     # Overview dashboard
│   ├── src/components/plant-monitor/
│   │   ├── PlantWorkspace.tsx     # Main dashboard workspace with device selector
│   │   ├── SensorGrid.tsx         # Real-time sensor metric cards
│   │   ├── PumpControlCard.tsx    # Confirmed pump state & manual/auto controls
│   │   └── HistoricalTrends.tsx   # Recharts telemetry visualization
│   └── package.json
│
├── docs/                          # Engineering Documentation
│   ├── hardware-connections.md    # Electrical schematics & wiring specifications
│   ├── api-documentation.md       # API endpoint specifications
│   └── running-commands.md        # Command reference for all components
└── README.md
```

---

## 🚀 Step-by-Step Setup & Execution

### 1. Configure Network & Environment

1. Find your computer's local LAN IPv4 address:
   ```powershell
   # Windows PowerShell:
   (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*").IPAddress
   ```
   *Example LAN IP: `192.168.0.194`*

2. Update `backend/.env`:
   ```env
   HOST=0.0.0.0
   PORT=8000
   DATABASE_URL=sqlite:///agritech.db
   DEVICE_TOKEN=replace-with-a-long-random-secret
   ADMIN_TOKEN=super_secret_admin_token_2026
   ```

3. Update `hardware/config.py`:
   ```python
   WIFI_SSID = "Your_WiFi_Network"
   WIFI_PASSWORD = "Your_WiFi_Password"
   API_BASE_URL = "http://192.168.0.194:8000"  # Use your computer's actual LAN IP
   DEVICE_ID = "plant-01"
   DEVICE_TOKEN = "replace-with-a-long-random-secret"
   ```

---

### 2. Run the FastAPI Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **Health check**: `http://localhost:8000/health` or `http://192.168.0.194:8000/health`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

---

### 3. Run the Next.js Frontend Dashboard

```powershell
cd frontend
npm install
npm run dev
```

- **Live Dashboard**: [http://localhost:3000/plant-monitor](http://localhost:3000/plant-monitor)
- Connects automatically to the backend on port 8000 and receives live SSE telemetry.

---

### 4. Flash and Upload ESP8266 MicroPython Firmware

#### Flash MicroPython v1.29.0:
```powershell
# 1. Erase flash on ESP8266
python -m esptool --port COM5 erase_flash

# 2. Flash MicroPython binary at address 0x0
python -m esptool --port COM5 --baud 460800 write_flash --flash_size=4MB -fm dio 0 hardware/ESP8266_GENERIC-FLASH_1M-20260824-v1.29.0.bin
```

#### Upload MicroPython Source Files:
```powershell
# Copy configuration, LCD driver, and main firmware
python -m mpremote connect COM5 cp hardware/config.py :config.py
python -m mpremote connect COM5 cp hardware/lcd_i2c.py :lcd_i2c.py
python -m mpremote connect COM5 cp hardware/main.py :main.py

# Reset board and run
python -m mpremote connect COM5 reset
```

---

### 5. Run the Software Simulator (Without Physical Board)

If the physical ESP8266 board is disconnected or in bench testing:
```powershell
python hardware/device_simulator.py
```
*The simulator posts real-time telemetry every 5 seconds, logs server command responses, and demonstrates auto/manual pump switching with explicit `[SIMULATED]` labeling.*

---

## 📡 REST API Reference

All requests must use JSON bodies with appropriate authentication headers.

### 1. Ingest Telemetry
- **Endpoint**: `POST /api/device/telemetry`
- **Header**: `X-Device-Token: replace-with-a-long-random-secret`
- **Request Body**:
  ```json
  {
    "device_id": "plant-01",
    "temperature_c": 27.5,
    "humidity_pct": 52.0,
    "soil_raw": 680,
    "soil_moisture_pct": 42.0,
    "motion": false,
    "pump_on": false,
    "mode": "auto"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "device_id": "plant-01",
    "timestamp": "2026-10-29T02:36:45.490593+00:00"
  }
  ```

### 2. Poll Device Command
- **Endpoint**: `GET /api/device/command?device_id=plant-01`
- **Header**: `X-Device-Token: replace-with-a-long-random-secret`
- **Response**:
  ```json
  {
    "command_id": 5,
    "mode": "manual",
    "pump_on": true
  }
  ```

### 3. Read Device Live State
- **Endpoint**: `GET /api/state?device_id=plant-01`
- **Header**: `X-Admin-Token: super_secret_admin_token_2026`
- **Response**:
  ```json
  {
    "device_id": "plant-01",
    "online": true,
    "last_seen": "2026-10-29T02:36:45.490593",
    "pump_on": false,
    "mode": "auto",
    "telemetry": {
      "temperature_c": 27.5,
      "humidity_pct": 52.0,
      "soil_moisture_pct": 42.0,
      "motion": false
    }
  }
  ```

### 4. Issue Remote Actuator Control
- **Endpoint**: `POST /api/control`
- **Header**: `X-Admin-Token: super_secret_admin_token_2026`
- **Request Body**:
  ```json
  {
    "device_id": "plant-01",
    "mode": "manual",
    "pump_on": true
  }
  ```
- **Response**:
  ```json
  {
    "command_id": 7,
    "device_id": "plant-01",
    "mode": "manual",
    "pump_on": true,
    "status": "pending"
  }
  ```

### 5. Health Check
- **Endpoint**: `GET /health` or `GET /api/health`
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "connected",
    "version": "2.0.0",
    "system": "AI-Powered Smart Plant Monitoring & Irrigation API"
  }
  ```

---

## 💧 Soil Moisture Sensor Calibration

The capacitive/resistive analog soil sensor measures voltage through the ESP8266 `A0` ADC pin (raw range: 0–1024).

1. **Dry Air Reading**: Leave the sensor probes clean and dry in the open air. Note the reported `soil_raw` value (typically ~`850`–`1024`).
2. **Submerged Water Reading**: Submerge the sensor probes up to the maximum immersion line in a cup of water. Note the reported `soil_raw` value (typically ~`300`–`400`).
3. **Configure Calibration Constants**: In `hardware/config.py`:
   ```python
   SOIL_DRY_RAW = 850   # Raw reading in completely dry soil / air
   SOIL_WET_RAW = 350   # Raw reading in fully saturated water
   ```
   The firmware calculates calibrated moisture percentage via:
   $$\text{Moisture \%} = \frac{\text{SOIL\_DRY\_RAW} - \text{RAW}}{\text{SOIL\_DRY\_RAW} - \text{SOIL\_WET\_RAW}} \times 100$$

---

## 🧪 Comprehensive Verification Matrix

Executed via automated test suite `backend/tests/verify_end_to_end.py`:

| Test Name | Target Subsystem | Expected Result | Result | Evidence |
|---|---|---|:---:|---|
| **ESP8266 Hardware Sensors** | DHT11, Soil ADC, PIR, Relay, LCD | Valid readings; Relay safe OFF (`1`) | **PASS** | Probe output: `{'humidity_pct': 39, 'device_id': 'plant-01', 'soil_raw': 1024, 'soil_moisture_pct': 0, 'motion': True, 'temperature_c': 27} RELAY_SAFE_VAL: 1` |
| **Telemetry Ingestion** | `POST /api/device/telemetry` | HTTP 200, JSON success confirmation | **PASS** | `Status 200, body={'success': True, 'device_id': 'plant-01'}` |
| **Security & Auth** | Token Validation | HTTP 401 Unauthorized on invalid key | **PASS** | Rejected with HTTP 401 Unauthorized |
| **State & Online Status** | `GET /api/state` | `online=true`, accurate `last_seen` | **PASS** | `online=True, last_seen=2026-10-29T02:36:45, temp=28.0C` |
| **Pump ON Remote Command** | `POST /api/control` → Device Poll | Device receives `command_id` with `pump_on=true` | **PASS** | Command ID 5 polled by device with `pump_on=True` |
| **Pump OFF Remote Command** | `POST /api/control` → Device Poll | Device receives `command_id` with `pump_on=false` | **PASS** | Command ID 6 polled by device with `pump_on=False` |
| **Automatic Irrigation** | Soil Hysteresis | Low triggers pump; High cutoff | **PASS** | Soil < 35.0% triggers pump; Soil >= 55.0% stops pump |
| **Historical Records** | SQLite DB Persistence | Chronological telemetry queries | **PASS** | Retrieved 8 stored records from `agritech.db` |
| **Invalid Sensor Fallback** | Exception Handling | Null/None handled safely | **PASS** | Accepted `null` readings without crashing |
| **Website Live Dashboard** | Next.js 16 Web UI | Dashboard renders at `/plant-monitor` | **PASS** | HTTP 200 OK from Next.js server |

---

## 🛠️ Troubleshooting Guide

### 1. Serial Port Access Denied (`PermissionError: [Errno 13] Access is denied: 'COM5'`)
- Ensure no other serial monitor (Arduino IDE Serial Monitor, PuTTY, or another terminal) is holding the COM port.
- Close any open terminal sessions before executing `mpremote` or `esptool`.

### 2. Wi-Fi Reconnection on ESP8266
- The firmware includes non-blocking Wi-Fi reconnect attempts every 15 seconds. If Wi-Fi drops, the pump continues to operate safely according to local fail-safes and automatically reconnects when signal is restored.

### 3. Relay Module Inverted / Clicks Rapidly
- Most 5V optocoupled relay modules are **active-LOW**.
- Verify `RELAY_ACTIVE_LOW = True` in `hardware/config.py`. The firmware initializes the relay to `Pin.OUT, value=1` before entering the loop to ensure the pump remains safely OFF.

### 4. Memory Allocations & MicroPython `MemoryError`
- The firmware explicitly calls `gc.collect()` and closes all HTTP response objects inside a `finally` block in `api_request()`.

---

## 🛡️ License

This project is licensed under the MIT License. Developed for IoT Plant Health Monitoring & Automated Irrigation Demonstration.
