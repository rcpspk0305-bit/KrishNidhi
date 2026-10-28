from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    api_key_hash = Column(String(128), nullable=False)
    status = Column(String(32), default="offline")  # online, offline, fault
    control_mode = Column(String(16), default="AUTO") # AUTO, MANUAL, OFF
    pump_state = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
    commands = relationship("DeviceCommand", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    plant_profile = relationship("PlantProfile", back_populates="device", uselist=False, cascade="all, delete-orphan")
    pump_events = relationship("PumpEvent", back_populates="device", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Core Smart Plant IoT Sensors
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)  # Calibrated 0-100%
    soil_raw = Column(Integer, nullable=True)       # Raw ADC value (0-1023)
    motion_detected = Column(Boolean, default=False)
    pump_on = Column(Boolean, default=False)
    control_mode = Column(String(16), default="AUTO")
    
    # Extended agronomy attributes (retained for backward compatibility)
    ph = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    n = Column(Float, nullable=True)
    p = Column(Float, nullable=True)
    k = Column(Float, nullable=True)
    tds = Column(Float, nullable=True)

    device = relationship("Device", back_populates="readings")

    __table_args__ = (
        Index("ix_readings_device_time", "device_id", "timestamp"),
    )


class PumpEvent(Base):
    __tablename__ = "pump_events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    requested_state = Column(Boolean, nullable=False)
    confirmed_state = Column(Boolean, nullable=False)
    source = Column(String(32), default="auto")  # auto, manual_button, web_command, safety_override
    control_mode = Column(String(16), default="AUTO")
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True)

    device = relationship("Device", back_populates="pump_events")


class DeviceCommand(Base):
    __tablename__ = "commands"

    id = Column(String(64), primary_key=True, index=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    action = Column(String(32), nullable=False)  # SET_PUMP, SET_MODE, CALIBRATE, REBOOT
    value = Column(String(128), nullable=False)  # "true", "false", "AUTO", "MANUAL", "OFF"
    status = Column(String(32), default="PENDING")  # PENDING, APPLIED, REJECTED, EXPIRED, FAILED
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    executed_at = Column(DateTime, nullable=True)

    device = relationship("Device", back_populates="commands")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    type = Column(String(64), nullable=False)  # SOIL_DRY, HIGH_TEMP, SENSOR_FAULT, PUMP_SAFETY, MOTION_ALERT
    severity = Column(String(16), default="medium")  # info, low, medium, high, critical
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)

    device = relationship("Device", back_populates="alerts")


class PlantProfile(Base):
    __tablename__ = "plant_profiles"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False)
    plant_name = Column(String(128), default="Tomato (Solanum lycopersicum)")
    plant_type = Column(String(64), default="Vegetable")
    preferred_temp_min = Column(Float, default=18.0)
    preferred_temp_max = Column(Float, default=30.0)
    preferred_humidity_min = Column(Float, default=50.0)
    preferred_humidity_max = Column(Float, default=70.0)
    preferred_moisture_min = Column(Float, default=30.0)  # Irrigation trigger
    preferred_moisture_max = Column(Float, default=65.0)  # Irrigation stop
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    device = relationship("Device", back_populates="plant_profile")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="operator")  # admin, operator, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
