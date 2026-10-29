# Application Run Commands & Operational Manual

This document provides a consolidated, exhaustive reference of all execution, build, test, and verification commands across every subsystem in the **AI-Powered Smart Plant Monitoring & Irrigation Platform** (NRCM-Codestrom).

---

## 🧭 Subsystem Quick Reference Matrix

| Subsystem | Working Directory | Default Host & Port | Primary Run Command | Health / Entry Endpoint |
|---|---|---|---|---|
| **FastAPI Backend** | `backend/` | `http://localhost:8000` | `uvicorn app.main:app --reload --port 8000` | `http://localhost:8000/docs` |
| **Next.js Web Frontend** | `frontend/` | `http://localhost:3000` | `npm run dev` | `http://localhost:3000/plant-monitor` |
| **Streamlit Operations Portal** | Repository Root (`.`) | `http://localhost:8501` | `streamlit run streamlit_app.py` | `http://localhost:8501` |
| **Docker Compose Stack** | Repository Root (`.`) | `3000` (Web), `8000` (API) | `docker compose up --build -d` | `http://localhost:3000` |
| **Backend Test Suite** | `backend/` | N/A | `python -m pytest tests -v` | CLI test report (20 passing) |
| **Frontend Test Suite** | `frontend/` | N/A | `npm test` | Node test runner output |
| **Assistant Readiness Check** | `backend/` | N/A | `python -m scripts.check_assistant` | CLI readiness status |
| **ESP8266 Firmware** | `firmware/smart_plant/` | Serial COM / 115200 baud | `arduino-cli compile` / `upload` | Serial Monitor output |

---

## 1. Prerequisites & Environment Setup

### 1.1 Python Virtual Environment (Backend & Streamlit)

From repository root or `backend/`:

```bash
# Create a virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Activate on Windows (CMD):
venv\Scripts\activate.bat

# Activate on Linux / macOS:
source venv/bin/activate
```

#### Install Backend & Streamlit Dependencies

```bash
# Option A: Install backend dependencies only
cd backend
pip install -r requirements.txt

# Option B: Install root dependencies (includes Streamlit, Plotly, Pandas, Pillow)
cd ..
pip install -r requirements.txt
```

### 1.2 Node.js Environment (Next.js Frontend)

From `frontend/`:

```bash
cd frontend
npm install
```

### 1.3 Environment Variables Configuration

#### Backend Configuration (`backend/.env`)

Copy `backend/.env.example` to `backend/.env`:

```bash
# Windows (PowerShell):
Copy-Item backend\.env.example backend\.env

# Linux / macOS:
cp backend/.env.example backend/.env
```

Key variables inside `backend/.env`:
```env
# Database configuration (SQLite default)
DATABASE_URL=sqlite:///agritech.db

# Edge authentication salt & JWT signing
DEVICE_SECRET_SALT=krishinidhi_smart_plant_salt_2026
JWT_SECRET=super_secret_jwt_key_change_in_prod

# Optional AI Providers
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/free
ASSISTANT_REQUESTS_PER_MINUTE=6
ASSISTANT_DAILY_REQUEST_LIMIT=200

# Optional Twilio SMS Integration
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
TWILIO_TO_NUMBER=
```

#### Frontend Configuration (`frontend/.env.local`)

Create or update `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 2. FastAPI Backend Service

All commands in this section should be executed from the `backend/` directory:

```bash
cd backend
```

### 2.1 Start Development Server (Hot Reload)

```bash
# Using uvicorn CLI (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using python module execution
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 Start Production Server (Multi-Worker)

```bash
# Run with 4 Uvicorn worker processes
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2.3 Verify API Availability

- **Interactive OpenAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Root Health Check**: [http://localhost:8000/](http://localhost:8000/)

### 2.4 Assistant Readiness Diagnostic Script

Test the live status of the multilingual floating assistant provider:

```bash
cd backend
python -m scripts.check_assistant
```

---

## 3. Next.js Web Frontend Application

All commands in this section should be executed from the `frontend/` directory:

```bash
cd frontend
```

### 3.1 Start Development Server

```bash
npm run dev
```
The application will be live at [http://localhost:3000](http://localhost:3000).
- Primary dashboard: [http://localhost:3000/plant-monitor](http://localhost:3000/plant-monitor)
- Legacy dashboard alias: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- Government Scheme Finder: [http://localhost:3000/scheme-finder](http://localhost:3000/scheme-finder)

### 3.2 Production Build & Execution

```bash
# 1. Compile Next.js 16 production bundle (strict typecheck + optimizations)
npm run build

# 2. Start optimized production server on port 3000
npm start
```

### 3.3 Linting & Static Code Quality

```bash
npm run lint
```

### 3.4 Interface Localization Script

Run the safe, AST-based UI localization script:

```bash
node scripts/localize-interface.cjs
```

---

## 4. Streamlit Operations & ML Analytics Portal

> [!IMPORTANT]
> **Working Directory Notice**: Streamlit **must** be executed from the **repository root** (`NRCM-Codestrom/`), not from inside `backend/`. This ensures backend models, database sessions, and services are correctly resolved on Python's path.

### 4.1 Launch Streamlit Application

```bash
# From repository root:
streamlit run streamlit_app.py
```
Or via python module:
```bash
python -m streamlit run streamlit_app.py
```

### 4.2 Launch with Custom Port / Network Binding

```bash
# Bind to all network interfaces on port 8501
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Run in headless mode (ideal for background services or servers)
streamlit run streamlit_app.py --server.headless true --server.port 8501
```

Access the Streamlit portal at [http://localhost:8501](http://localhost:8501).

---

## 5. Automated Software Testing Suites

### 5.1 Backend Pytest Suite

Run all 20 backend unit, integration, and workflow tests:

```bash
# Option 1: From backend directory (recommended)
cd backend
python -m pytest tests -v

# Option 2: From repository root
python -m pytest backend/tests -v
```

#### Run Specific Test Modules

```bash
cd backend

# Telemetry ingestion & threshold alerts
python -m pytest tests/test_telemetry.py -v

# Actuator commands, polling, and ACK loop
python -m pytest tests/test_pump_control.py -v

# Device registration and API key hashing
python -m pytest tests/test_devices.py -v

# Deterministic VPD calculation and agronomic rules
python -m pytest tests/test_analytics.py -v

# Direct microcontroller endpoints & pump historical tracking
python -m pytest tests/test_direct_api_and_pump_history.py -v

# Headless Streamlit AppTest workflows
python -m pytest tests/test_streamlit_workflows.py -v

# Multilingual floating assistant and admission limits
python -m pytest tests/test_assistant.py -v
```

### 5.2 Frontend Automated Node.js Tests

Run all unit tests in the frontend test suite:

```bash
cd frontend
npm test
```

This runs:
```bash
node --test tests/plant-state.test.mjs tests/i18n.test.mjs
```

#### Run Individual Frontend Test Files

```bash
cd frontend

# Plant state & telemetry calculations test
node --test tests/plant-state.test.mjs

# Multilingual catalog completeness test (en, te, hi)
node --test tests/i18n.test.mjs
```

---

## 6. Docker Container Orchestration

Run the complete multi-container stack (FastAPI Backend + Next.js Frontend) using Docker Compose from the repository root:

### 6.1 Build and Start Entire Stack

```bash
# Build images and start containers in detached mode
docker compose up --build -d
```

### 6.2 Monitor Container Status & Logs

```bash
# Check container status
docker compose ps

# Follow logs from all services
docker compose logs -f

# Follow backend service logs only
docker compose logs -f backend

# Follow frontend service logs only
docker compose logs -f frontend
```

### 6.3 Stop and Clean Up Containers

```bash
# Stop containers without removing persisted volumes
docker compose down

# Stop containers and remove persisted backend database volume
docker compose down -v
```

---

## 7. Database Administration & Schemas

### 7.1 SQLite Database (Default)

The backend automatically creates and seeds `backend/agritech.db` on startup via SQLAlchemy `init_db()`.

To inspect tables and data via SQLite CLI:
```bash
# From backend directory:
sqlite3 agritech.db ".tables"
sqlite3 agritech.db "SELECT id, name, status, control_mode FROM devices;"
sqlite3 agritech.db "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 5;"
```

### 7.2 PostgreSQL Database (Optional Production Target)

To initialize a PostgreSQL instance using the provided schema:
```bash
psql -h localhost -U postgres -d agritech -f database/postgres-schema.sql
```

Update `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/agritech
```

### 7.3 MongoDB Initialization (Optional Companion)

To initialize MongoDB collections and indices:
```bash
mongosh database/mongo-init.js
```

---

## 8. Firmware Flashing & Hardware Operations (ESP8266)

The firmware is located in `firmware/smart_plant/smart_plant.ino`.

### 8.1 Arduino IDE (GUI Method)

1. Open `firmware/smart_plant/smart_plant.ino` in Arduino IDE 2.x.
2. Select Board: **NodeMCU 1.0 (ESP-12E Module)**.
3. Configure `firmware/smart_plant/config.h`:
   - Set `WIFI_DEFAULT_SSID` and `WIFI_DEFAULT_PASS`.
   - Set `SERVER_BASE_URL` to your backend machine's LAN IP (e.g. `http://192.168.1.50:8000/api`).
4. Connect via micro-USB, select the appropriate COM/TTY port, and click **Upload** (115200 baud).

### 8.2 Arduino CLI (Terminal Method)

```bash
# 1. Install ESP8266 board core
arduino-cli core update-index
arduino-cli core install esp8266:esp8266

# 2. Compile firmware sketch
arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 firmware/smart_plant/smart_plant.ino

# 3. Upload to connected board (replace COM3 with your actual port)
arduino-cli upload -p COM3 --fqbn esp8266:esp8266:nodemcuv2 firmware/smart_plant/smart_plant.ino

# 4. Open serial monitor at 115200 baud
arduino-cli monitor -p COM3 --config baudrate=115200
```

---

## 9. API Smoke Testing via cURL & PowerShell

Test the running backend API directly from the command line:

### 9.1 Root Healthcheck
```bash
# bash / macOS:
curl -s http://localhost:8000/ | jq .

# PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/"
```

### 9.2 Ingest Direct ESP8266 Telemetry
```bash
# bash:
curl -X POST http://localhost:8000/api/devices/esp8266-plant-01/telemetry \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: default_secret_key_123" \
  -d '{"temperature": 25.2, "humidity": 62.0, "soil_moisture": 45.0, "raw_adc": 580, "motion": false}'

# PowerShell:
$headers = @{ "X-Device-Key" = "default_secret_key_123"; "Content-Type" = "application/json" }
$body = '{"temperature": 25.2, "humidity": 62.0, "soil_moisture": 45.0, "raw_adc": 580, "motion": false}'
Invoke-RestMethod -Uri "http://localhost:8000/api/devices/esp8266-plant-01/telemetry" -Method Post -Headers $headers -Body $body
```

### 9.3 Poll Pending Actuation Command
```bash
curl -s -H "X-Device-Key: default_secret_key_123" http://localhost:8000/api/devices/esp8266-plant-01/commands
```

### 9.4 Acknowledge Hardware Command Execution
```bash
curl -X POST http://localhost:8000/api/devices/esp8266-plant-01/ack \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: default_secret_key_123" \
  -d '{"command_id": 1, "applied": true, "relay_state": true, "reason": "Watering started"}'
```

### 9.5 Test Floating Multilingual Assistant
```bash
curl -X POST http://localhost:8000/api/v1/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is optimal soil moisture for Monstera?", "language": "en"}'
```

### 9.6 Listen to Real-Time SSE Stream
```bash
curl -N http://localhost:8000/api/v1/events/stream
```

---

## 10. Troubleshooting & Port Conflict Management

If a service fails to start due to port conflicts:

### 10.1 Port Conflict Resolution on Windows (PowerShell)

```powershell
# Check which process is occupying port 8000, 3000, or 8501
Get-NetTCPConnection -LocalPort 8000, 3000, 8501 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess, State

# Or using netstat:
netstat -ano | findstr :8000
netstat -ano | findstr :3000
netstat -ano | findstr :8501

# Terminate process holding the port (replace <PID> with process ID):
Stop-Process -Id <PID> -Force
# Or via taskkill:
taskkill /PID <PID> /F
```

### 10.2 Port Conflict Resolution on Linux / macOS

```bash
# Find process ID occupying port
lsof -i :8000
lsof -i :3000
lsof -i :8501

# Terminate process holding port
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
kill -9 $(lsof -t -i:8501)
```

---

## 11. Cross-Reference Links

- Architecture Documentation: [docs/architecture.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/architecture.md)
- Subsystems Overview: [docs/codebase-overview.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/codebase-overview.md)
- Deployment Guide: [docs/deployment.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/deployment.md)
- Verification & Test Guide: [docs/testing.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/testing.md)
- Hardware Connections: [docs/hardware-connections.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/hardware-connections.md)
- Multilingual Assistant Details: [docs/multilingual-assistant.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/multilingual-assistant.md)
