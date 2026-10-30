from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class SensorData(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    N: float = Field(ge=0, le=1000)
    P: float = Field(ge=0, le=1000)
    K: float = Field(ge=0, le=1000)
    temperature: float = Field(ge=-40, le=80)
    humidity: float = Field(ge=0, le=100)
    ph: float = Field(ge=0, le=14)
    rainfall: float = Field(ge=0, le=10000)
    tds: float = Field(ge=0, le=10000)

class IoTTelemetryInput(BaseModel):
    temperature: Optional[float] = None
    temp: Optional[float] = None
    humidity: Optional[float] = None
    hum: Optional[float] = None
    ph: Optional[float] = None
    rainfall: Optional[float] = None
    rain: Optional[float] = None
    tds: Optional[float] = None
    N: Optional[float] = None
    n: Optional[float] = None
    P: Optional[float] = None
    p: Optional[float] = None
    K: Optional[float] = None
    k: Optional[float] = None
    device_id: Optional[str] = "esp32-node-01"

class IoTStatusResponse(BaseModel):
    status: str
    connected: bool
    device_id: str
    source: str
    last_packet_time: Optional[str] = None
    packet_count: int
    data: dict

class GenAIRequest(BaseModel):
    crop: str
    disease: str
    sensor_data: dict
    language: str = "English"

class ChatRequest(BaseModel):
    message: str
    history: list = []
    language: str = "English"

class TrendPoint(BaseModel):
    slot: str
    temperature: float
    humidity: float

class DashboardMetric(BaseModel):
    label: str
    value: float
    unit: str
    trend: float

class DashboardWindow(BaseModel):
    id: str
    title: str
    status: str
    summary: str

class DashboardOverviewResponse(BaseModel):
    status: str
    generated_at: str
    theme: str
    health_score: int
    metrics: List[DashboardMetric]
    trend: List[TrendPoint]
    windows: List[DashboardWindow]

class DashboardWindowResponse(BaseModel):
    status: str
    window: str
    title: str
    payload: dict
