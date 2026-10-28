# Deployment & Installation Guide

This guide covers local development, Docker multi-container deployment, and production hardening for the **AI-Powered Smart Plant Monitoring System**.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.12+ (Python 3.14 compatible)
- Node.js 18+ and npm
- Arduino IDE 2.x (for flashing ESP8266)

### 1.1 Backend Setup (FastAPI)
1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `backend/.env`:
   ```env
   DATABASE_URL=sqlite:///agritech.db
   DEVICE_SECRET_SALT=my_secure_device_salt_2026
   JWT_SECRET=my_jwt_production_secret_key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - API Docs will be available at: `http://localhost:8000/docs`
   - Base API v1 endpoint: `http://localhost:8000/api/v1`

---

### 1.2 Frontend Setup (Next.js)
1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables in `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```
4. Start Next.js development server:
   ```bash
   npm run dev
   ```
   - Dashboard will be available at: `http://localhost:3000/plant-monitor`

---

## 2. Docker Compose Deployment

The monorepo includes a complete `docker-compose.yml` to spin up both the FastAPI backend and Next.js frontend in isolated containers.

To build and start the entire stack:
```bash
docker compose up --build -d
```

- **Frontend Dashboard**: `http://localhost:3000/plant-monitor`
- **FastAPI Backend**: `http://localhost:8000/docs`

To view logs:
```bash
docker compose logs -f
```

To stop containers:
```bash
docker compose down
```

---

## 3. Production Hardening & Reverse Proxy (Nginx)

When deploying to a remote VPS (e.g. AWS EC2, DigitalOcean, Hetzner), terminate TLS with Nginx:

```nginx
server {
    listen 80;
    server_name plant.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name plant.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/plant.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/plant.yourdomain.com/privkey.pem;

    # Next.js Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI REST API & SSE Events
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CRITICAL FOR SERVER-SENT EVENTS (SSE):
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
        chunked_transfer_encoding off;
    }
}
```

---

## 4. Environment Variables Reference

| Variable | Scope | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Backend | `sqlite:///agritech.db` | SQLAlchemy connection string (SQLite or PostgreSQL) |
| `DEVICE_SECRET_SALT` | Backend | `krishinidhi_smart_plant_salt_2026` | Cryptographic salt used for hashing ESP8266 API keys |
| `JWT_SECRET` | Backend | `super_secret_jwt_key` | Secret key for JWT session validation |
| `GEMINI_API_KEY` | Backend | *(Optional)* | Google Gemini API key for natural language explanations |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000/api/v1` | Publicly reachable API base URL |
