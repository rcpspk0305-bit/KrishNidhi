---
title: "Comprehensive Application Run Commands and Runtime Workflows"
date: "2026-10-29"
category: "developer-experience"
module: "developer_experience"
problem_type: "developer_experience"
component: "development_workflow"
severity: "low"
applies_when:
  - "Starting, building, testing, or deploying any subsystem in the NRCM-Codestrom repository"
  - "Troubleshooting port conflicts or runtime execution errors across FastAPI, Next.js, and Streamlit"
  - "Onboarding new developers or setting up automated CI/CD pipelines"
symptoms:
  - "Fragmented command references across multiple READMEs and documentation guides"
  - "Streamlit failing on startup when launched from inside backend/ rather than project root"
  - "Port collisions when running FastAPI (8000), Next.js (3000), and Streamlit (8501) concurrently"
root_cause: "inadequate_documentation"
resolution_type: "documentation_update"
tags:
  - "run-commands"
  - "developer-experience"
  - "fastapi"
  - "nextjs"
  - "streamlit"
  - "docker"
  - "testing"
related_components:
  - "backend"
  - "frontend"
  - "streamlit"
  - "firmware"
  - "infrastructure"
---

# Comprehensive Application Run Commands and Runtime Workflows

## Context
The NRCM-Codestrom repository is a heterogeneous multi-tier IoT and AgriTech solution consisting of:
1. **Edge Firmware (`firmware/smart_plant/`)**: C++ Arduino sketch for ESP8266 NodeMCU.
2. **Backend API (`backend/`)**: Asynchronous FastAPI server with SQLite/PostgreSQL, SSE broadcaster, and Gemini/OpenRouter AI services.
3. **Frontend Dashboard (`frontend/`)**: Modern Next.js 16 + React 19 web application.
4. **Operations Portal (`streamlit_app.py`)**: Multi-tab data science and live IoT diagnostics application.
5. **Container Stack (`docker-compose.yml`)**: Multi-container Docker orchestration for unified deployment.

Previously, running instructions were split across `README.md`, `docs/deployment.md`, `docs/testing.md`, and individual subdirectories, creating friction for operators and developers needing rapid command lookup.

## Guidance & Command Reference

### 1. Unified Subsystem Execution

| Subsystem | Directory | Command | Default Port / URL |
|---|---|---|---|
| **FastAPI Backend** | `backend/` | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | `http://localhost:8000/docs` |
| **Next.js Web UI** | `frontend/` | `npm run dev` | `http://localhost:3000/plant-monitor` |
| **Streamlit Operations** | Repo Root (`.`) | `streamlit run streamlit_app.py` | `http://localhost:8501` |
| **Docker Compose** | Repo Root (`.`) | `docker compose up --build -d` | Web: `3000`, API: `8000` |

### 2. Execution Nuances & Critical Invariants

1. **Streamlit Working Directory**: Streamlit must be executed from the **repository root** (`NRCM-Codestrom/`), not from within `backend/`. `streamlit_app.py` programmatically appends `backend` to `sys.path` to import database models and services. Running from inside `backend/` leads to `ModuleNotFoundError` or failed database initialization.
2. **Backend Port & Host Binding**: Running with `--host 0.0.0.0` allows physical ESP8266 microcontrollers and mobile browsers on the local LAN to stream telemetry to the backend at your machine's local IP (e.g. `192.168.x.x:8000`).
3. **Environment Isolation**:
   - Backend requires `backend/.env` containing `DATABASE_URL`, `DEVICE_SECRET_SALT`, and optionally `GEMINI_API_KEY` or `OPENROUTER_API_KEY`.
   - Frontend requires `frontend/.env.local` containing `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

### 3. Key Examples

#### Backend Execution & Diagnostics
```bash
# Start FastAPI backend with hot reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run assistant live readiness check
python -m scripts.check_assistant

# Execute pytest backend test suite (20 passing tests)
python -m pytest tests -v
```

#### Frontend Execution & Build
```bash
cd frontend

# Start Next.js 16 development server
npm run dev

# Compile production build
npm run build

# Run node unit test runner (plant-state & i18n tests)
npm test
```

#### Streamlit Operations Portal
```bash
# Always execute from project root
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

#### Full Stack Docker Compose
```bash
# Build and run detached
docker compose up --build -d

# View live streaming logs
docker compose logs -f

# Teardown
docker compose down
```

#### Port Conflict Resolution (Windows PowerShell)
```powershell
# Identify processes occupying ports 8000, 3000, or 8501
Get-NetTCPConnection -LocalPort 8000, 3000, 8501 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess, State

# Terminate offending PID
Stop-Process -Id <PID> -Force
```

## Applicability Note
Use the consolidated runbook at [docs/running-commands.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/running-commands.md) as the primary manual for operators, developers, and CI/CD automation runners.

## Related
- Run Commands Manual: [docs/running-commands.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/running-commands.md)
- Subsystems Architecture: [docs/solutions/architecture-patterns/codebase-architecture-and-subsystems.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/solutions/architecture-patterns/codebase-architecture-and-subsystems.md)
- Deployment Guide: [docs/deployment.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/deployment.md)
- Testing Guide: [docs/testing.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/testing.md)
- Architecture Overview: [docs/architecture.md](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/docs/architecture.md)
