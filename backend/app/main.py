import threading
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sensors, predict, chat, sms, dashboard
from app.services.mqtt_service import start_mqtt_background
from app.api.v1 import api_v1_router, api_router
from app.core.database import engine, init_db
from app.models import db_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agritech_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    init_db()
    
    # Pre-seed default demo device if none exists
    try:
        from app.core.database import SessionLocal
        from app.core.security import hash_api_key
        db = SessionLocal()
        default_dev = db.query(db_models.Device).filter(db_models.Device.id == "esp8266-plant-01").first()
        if not default_dev:
            logger.info("Seeding default demo device 'esp8266-plant-01'...")
            dev = db_models.Device(
                id="esp8266-plant-01",
                name="Main Indoor Greenhouse Planter",
                api_key_hash=hash_api_key("default_secret_key_123"),
                status="online",
                control_mode="AUTO",
                pump_state=False,
            )
            db.add(dev)
            db.flush()
            profile = db_models.PlantProfile(
                device_id="esp8266-plant-01",
                plant_name="Monstera Deliciosa",
                plant_type="Tropical Foliage",
                preferred_temp_min=18.0,
                preferred_temp_max=30.0,
                preferred_humidity_min=50.0,
                preferred_humidity_max=75.0,
                preferred_moisture_min=30.0,
                preferred_moisture_max=60.0,
            )
            db.add(profile)
            db.commit()
            logger.info("Default device and plant profile seeded successfully.")
        db.close()
    except Exception as e:
        logger.warning(f"Could not seed default device: {e}")

    # Start MQTT background subscriber if configured
    try:
        start_mqtt_background()
    except Exception as e:
        logger.warning(f"MQTT service background start skipped: {e}")

    yield

app = FastAPI(
    title="AI-Powered Smart Plant Monitoring & Irrigation API",
    description="Production-quality IoT Backend for ESP8266 NodeMCU, Soil Moisture, DHT11, PIR, 5V Relay Pump, and Next.js Dashboard.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Suite for Smart Plant Monitoring IoT (supports both /api/v1/devices and /api/devices)
app.include_router(api_v1_router)
app.include_router(api_router)

# Legacy / Companion Routes (Preserved for compatibility)
app.include_router(sensors.router)
app.include_router(predict.router)
app.include_router(chat.router)
app.include_router(sms.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "system": "AI-Powered IoT Smart Plant Monitoring & Irrigation API",
        "version": "2.0.0",
        "docs_url": "/docs",
        "api_v1_prefix": "/api/v1",
    }