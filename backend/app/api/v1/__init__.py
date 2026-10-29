from fastapi import APIRouter
from app.api.v1.devices import router as devices_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.pump import router as pump_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.events import router as events_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.device_compat import router as device_compat_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(devices_router)
api_v1_router.include_router(telemetry_router)
api_v1_router.include_router(pump_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(device_compat_router)

# Direct /api router for Section 5 compliance (/api/devices/...)
api_router = APIRouter(prefix="/api")
api_router.include_router(devices_router)
api_router.include_router(telemetry_router)
api_router.include_router(pump_router)
api_router.include_router(analytics_router)
api_router.include_router(alerts_router)
api_router.include_router(events_router)
api_router.include_router(assistant_router)
api_router.include_router(device_compat_router)

