# AI-Powered Smart Plant Monitoring & Automated Irrigation System

A complete, production-grade IoT plant monitoring and automated irrigation platform built with the **ESP8266 NodeMCU ESP-12E** microcontroller, a **FastAPI** backend with real-time Server-Sent Events (SSE), and a modern **Next.js 16** responsive dashboard.

---

## 🌟 Key Features

1. **Environmental Sensing**: Continuous non-blocking acquisition of Ambient Temperature & Relative Humidity (DHT11), Calibrated Soil Moisture percentage (LM393 AO + A0 ADC), and PIR Motion presence detection.
2. **Authoritative Pump Controller**: The ESP8266 microcontroller executes low-level irrigation logic with hardware fail-safes (15s maximum continuous runtime watchdog, 60s cooldown lockout, and sensor fault cutoffs).
3. **Three Operating Modes**:
   - `AUTO`: Autonomous soil moisture threshold irrigation (watering starts when moisture < 30%, stops when > 55%).
   - `MANUAL`: Controlled remotely via web dashboard switch or locally via debounced tactile push button.
   - `OFF`: Complete safety lockout.
4. **Local 16×2 I2C Display**: Rotates through 4 information screens every 3 seconds (Temp/Hum, Soil/Pump, WiFi/Server, Motion/Mode).
5. **Real-time Web Dashboard**: Built with Next.js, TypeScript, Tailwind CSS, and Recharts. Connected to backend via Server-Sent Events (SSE) for instant sub-second telemetry updates.
6. **AI Plant Health Analytics**: Deterministic agronomic rule engine calculating Vapor Pressure Deficit (VPD), thermal stress, and health scores (0–100), with optional Google Gemini natural language explanations.
7. **Virtual Hardware Simulator**: Built-in interactive simulator panel right inside the web dashboard to demonstrate telemetry, threshold alerts, and relay acknowledgments without needing physical hardware connected!
8. **Hardware Safety**: Relay initialized to safe inactive state *before* GPIO pin configuration to eliminate spurious reboot clicks.

---

## 📐 System Architecture

```text
DHT11 (D6) ──────┐
                 │
Soil Sensor (A0) ┼───────►  ESP8266 NodeMCU ESP-12E
                 │               │
PIR Motion (D7) ─┤       ┌───────┴────────┐
                 │       ▼                ▼
Push Button (D0) ┘  16x2 LCD (I2C)   5V Relay (D5) ──► 5V DC Submersible Pump
                         │                ▲
                         │   Wi-Fi (REST) │ (Poll & ACK)
                         ▼                │
                   FastAPI Backend Server (Port 8000)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  SQLite/Postgres   VPD Analytics   SSE Broadcaster
        │                │                │
        └────────────────┼────────────────┘
                         ▼
             Next.js Web Dashboard (Port 3000)
```

---

## 🔌 Hardware Pinout Mapping

| Component | ESP8266 Pin | GPIO | Voltage Level | Notes |
|---|---|---|---|---|
| **DHT11 DATA** | **D6** | `GPIO 12` | 3.3V | 1-Wire Digital protocol |
| **PIR OUT** | **D7** | `GPIO 13` | 3.3V Logic | Digital High upon motion |
| **Soil Moisture AO** | **A0** | `ADC 0` | 0.0V–3.3V | 10-sample moving average |
| **5V Relay IN** | **D5** | `GPIO 14` | 3.3V Logic | Active-LOW optocoupled input |
| **LCD SDA** | **D2** | `GPIO 4` | 3.3V Logic | I2C Data (Address 0x27) |
| **LCD SCL** | **D1** | `GPIO 5` | 3.3V Logic | I2C Clock |
| **Push Button** | **D0** | `GPIO 16` | 3.3V | Active-LOW (Internal pull-up) |

---

## 📂 Project Structure

```text
smart-plant-monitor/
├── firmware/
│   ├── smart_plant/
│   │   ├── smart_plant.ino        # Main cooperative multitasking sketch
│   │   ├── config.h               # Pin definitions, calibration, safety constants
│   │   ├── sensors.h              # DHT11, A0 ADC averaging, PIR readings
│   │   ├── pump_control.h         # Authoritative relay state machine & watchdog
│   │   ├── display.h              # 16x2 I2C LCD driver (4 rotating screens)
│   │   └── network.h              # Wi-Fi auto-reconnect, REST telemetry & ACK
│   └── README.md                  # Flashing guide & calibration instructions
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point & CORS configuration
│   │   ├── api/v1/                # Devices, telemetry, pump, analytics, alerts, SSE
│   │   ├── models/db_models.py    # SQLAlchemy models (Devices, Readings, Commands, Alerts)
│   │   ├── schemas/               # Pydantic v2 schemas
│   │   ├── services/              # SSE broadcaster, MQTT fallback
│   │   ├── analytics/             # Agronomic rule engine & Gemini advisor
│   │   └── core/                  # Database engine, cryptographic API key security
│   ├── tests/                     # Pytest automated test suite (14 passing tests)
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend container image
│   └── .env.example               # Environment variables template
│
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx               # Primary portal homepage
│   │   └── plant-monitor/page.tsx # Smart Plant Monitoring & Irrigation Dashboard
│   ├── src/components/plant-monitor/ # Health Hero, Sensor Cards, Pump Controls, Charts
│   ├── src/hooks/                 # usePlantMonitorSSE hook for real-time events
│   ├── src/lib/                   # Typed plantApi client
│   ├── src/types/                 # TypeScript interfaces
│   ├── Dockerfile                 # Next.js multi-stage container
│   └── package.json
│
├── docs/
│   ├── architecture.md            # Detailed end-to-end data flow & sequence diagrams
│   ├── hardware-connections.md    # Electrical schematics, logic levels & buck converter
│   ├── api-documentation.md       # Full OpenAPI/Swagger endpoint specifications
│   ├── deployment.md              # Local, Docker Compose & Nginx production setup
│   └── testing.md                 # Test execution logs & hardware physical checklist
│
├── docker-compose.yml             # Full-stack container orchestration
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Run the FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger): `http://localhost:8000/docs`
- Root Healthcheck: `http://localhost:8000/`

### 2. Run the Next.js Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:3000/plant-monitor`

### 3. Flash the ESP8266 NodeMCU Firmware
1. Open `firmware/smart_plant/smart_plant.ino` in Arduino IDE.
2. Update Wi-Fi credentials and server IP in `config.h`:
   ```cpp
   #define WIFI_DEFAULT_SSID "Your_WiFi_SSID"
   #define WIFI_DEFAULT_PASS "Your_WiFi_Password"
   #define SERVER_BASE_URL   "http://192.168.1.100:8000/api/v1"
   ```
3. Select board **NodeMCU 1.0 (ESP-12E Module)** and upload via USB at 115200 baud.

### 4. Run via Docker Compose (Alternative)
```bash
docker compose up --build -d
```

---

## 🧪 Verification & Testing Results

- **Backend Automated Tests**: 14 out of 14 unit and integration tests passing (`pytest tests -v` in 9.28s) covering telemetry validation, API key security, threshold alerts, command polling, ACK confirmation, and VPD calculation.
- **Frontend Build**: Next.js 16 build passed with 0 TypeScript errors.
- **Hardware Simulator**: Tested in browser with live telemetry updates and command ACKs.

---

## 🛡️ License

This project is licensed under the MIT License. Developed for Computer Science & Engineering IoT Project Demonstration.
