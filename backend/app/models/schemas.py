from pydantic import BaseModel
from typing import List, Optional

class SensorData(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    tds: float

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
