from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# ----------------- Device Schemas -----------------
class DeviceCreate(BaseModel):
    id: str = Field(..., min_length=3, max_length=64, description="Unique device identifier (e.g. esp8266-plant-01)")
    name: str = Field(..., min_length=1, max_length=128, description="Human friendly device label")
    api_key: Optional[str] = Field(None, min_length=8, description="Optional custom pre-shared device key. If omitted, one is generated.")

class DeviceResponse(BaseModel):
    id: str
    name: str
    status: str
    control_mode: str
    pump_state: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    api_key: Optional[str] = None  # Returned ONLY on initial registration

    model_config = ConfigDict(from_attributes=True)

class DeviceStatusResponse(BaseModel):
    device_id: str
    status: str
    online: bool
    control_mode: str
    pump_state: bool
    last_seen: Optional[datetime] = None
    seconds_since_last_seen: Optional[float] = None
    sensor_fault: bool = False
    active_alerts_count: int = 0
    last_watering_time: Optional[datetime] = None
    pump_runtime_seconds: Optional[int] = 0

# ----------------- Telemetry Schemas -----------------
class TelemetryCreate(BaseModel):
    temperature: Optional[float] = Field(None, ge=-40.0, le=80.0, description="Temperature in Celsius from DHT11")
    humidity: Optional[float] = Field(None, ge=0.0, le=100.0, description="Relative humidity in % from DHT11")
    soil_moisture: Optional[float] = Field(None, ge=0.0, le=100.0, description="Calibrated soil moisture percentage (0-100%)")
    soil_raw: Optional[int] = Field(None, ge=0, le=1023, description="Raw ADC 10-bit integer from soil sensor A0")
    motion_detected: bool = Field(False, description="True if PIR sensor detected motion")
    pump_on: bool = Field(False, description="Current physical state of the water pump relay")
    control_mode: str = Field("AUTO", description="Current operating mode (AUTO, MANUAL, OFF)")
    uptime_seconds: Optional[int] = Field(0, description="Device uptime since last boot in seconds")

class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    soil_moisture: Optional[float]
    soil_raw: Optional[int]
    motion_detected: bool
    pump_on: bool
    control_mode: str

    model_config = ConfigDict(from_attributes=True)

class TelemetryHistoryResponse(BaseModel):
    device_id: str
    total_records: int
    readings: List[TelemetryResponse]

# ----------------- Pump Control & Commands -----------------
class PumpControlRequest(BaseModel):
    action: str = Field(..., pattern="^(SET_PUMP|SET_MODE)$", description="SET_PUMP or SET_MODE")
    value: Any = Field(..., description="Boolean (true/false) for SET_PUMP, or String ('AUTO'/'MANUAL'/'OFF') for SET_MODE")
    ttl_seconds: Optional[int] = Field(60, ge=10, le=3600, description="Command time to live in seconds")

class DeviceCommandItem(BaseModel):
    command_id: str
    action: str
    value: Any
    created_at: datetime
    expires_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class CommandPollResponse(BaseModel):
    has_command: bool
    command_id: Optional[str] = None
    pump: Optional[bool] = None
    mode: Optional[str] = None
    command: Optional[DeviceCommandItem] = None

class CommandAckRequest(BaseModel):
    status: str = Field(..., pattern="^(APPLIED|REJECTED|FAILED)$")
    confirmed_state: Optional[bool] = None
    reason: Optional[str] = None

class CommandAckResponse(BaseModel):
    command_id: str
    status: str
    confirmed_state: Optional[bool]
    message: str

class PumpEventResponse(BaseModel):
    id: int
    device_id: str
    requested_state: bool
    confirmed_state: bool
    source: str
    control_mode: str
    reason: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Plant Profiles -----------------
class PlantProfileUpdate(BaseModel):
    plant_name: Optional[str] = None
    plant_type: Optional[str] = None
    preferred_temp_min: Optional[float] = None
    preferred_temp_max: Optional[float] = None
    preferred_humidity_min: Optional[float] = None
    preferred_humidity_max: Optional[float] = None
    preferred_moisture_min: Optional[float] = None
    preferred_moisture_max: Optional[float] = None

class PlantProfileResponse(BaseModel):
    device_id: str
    plant_name: str
    plant_type: str
    preferred_temp_min: float
    preferred_temp_max: float
    preferred_humidity_min: float
    preferred_humidity_max: float
    preferred_moisture_min: float
    preferred_moisture_max: float

    model_config = ConfigDict(from_attributes=True)

# ----------------- Alerts -----------------
class AlertResponse(BaseModel):
    id: int
    device_id: str
    type: str
    severity: str
    message: str
    acknowledged: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Analytics & Recommendations -----------------
class AnalyticsMetrics(BaseModel):
    avg_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    avg_soil_moisture: Optional[float] = None
    min_soil_moisture: Optional[float] = None
    current_vpd_kpa: Optional[float] = None  # Vapor Pressure Deficit
    watering_count_24h: int = 0
    total_watering_seconds_24h: int = 0
    dry_down_rate_pct_per_hr: Optional[float] = None

class AnalyticsResponse(BaseModel):
    device_id: str
    window_hours: int
    metrics: AnalyticsMetrics
    status_summary: str

class RecommendationResponse(BaseModel):
    language: str = "en"
    device_id: str
    plant_name: str
    health_score: int = Field(..., ge=0, le=100)
    status: str  # Optimal, Needs Attention, Critical
    health_status: Optional[str] = "Optimal"
    severity: str  # low, medium, high
    reason: Optional[str] = None
    recommendation: Optional[str] = None
    environmental_condition: Optional[str] = None
    moisture_assessment: Optional[str] = None
    temperature_assessment: Optional[str] = None
    humidity_assessment: Optional[str] = None
    recommended_actions: Optional[List[str]] = None
    observations: List[str]
    recommendations: List[str]
    ai_explanation: Optional[str] = None
    confidence: float = Field(0.95, ge=0.0, le=1.0)
    limitations: str
