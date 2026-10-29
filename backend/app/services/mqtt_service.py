import json
import logging
import threading
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

logger = logging.getLogger("agritech.mqtt")
logging.basicConfig(level=logging.INFO)

# Global in-memory storage for latest sensor values
latest_iot_data: Dict[str, Any] = {
    "N": 88.0,
    "P": 50.0,
    "K": 42.0,
    "temperature": 25.5,
    "humidity": 40.0,
    "ph": 6.8,
    "rainfall": 50.0,
    "tds": 150.0,
    "soil_moisture": 48.0,
    "soil_raw": 490,
    "motion_detected": False,
    "pump_on": False,
    "control_mode": "AUTO",
}

# Live connection metadata
iot_metadata: Dict[str, Any] = {
    "connected": False,
    "last_packet_time": None,
    "device_id": "esp32-node-01",
    "source": "standby",
    "packet_count": 0,
    "broker": "broker.hivemq.com:1883",
    "topic": "agritech/ps10/sensors",
}

_mqtt_lock = threading.Lock()
_mqtt_thread_started = False
_mqtt_client = None


def normalize_and_clamp(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and standardizes telemetry values regardless of naming conventions
    (e.g., handles 'temp', 'temperature', 'n', 'N', 'soil_moisture', etc.).
    """
    extracted: Dict[str, Any] = {}

    def extract_num(*keys: str, default: Optional[float] = None) -> Optional[float]:
        for k in keys:
            if k in payload and payload[k] is not None:
                try:
                    return float(payload[k])
                except (ValueError, TypeError):
                    pass
        return default

    # Temperature (°C)
    val = extract_num("temperature", "temp", "t")
    if val is not None:
        extracted["temperature"] = round(max(-10.0, min(65.0, val)), 1)

    # Humidity (%)
    val = extract_num("humidity", "hum", "h")
    if val is not None:
        extracted["humidity"] = round(max(0.0, min(100.0, val)), 1)

    # Soil pH (0 - 14)
    val = extract_num("ph", "pH", "PH")
    if val is not None:
        extracted["ph"] = round(max(0.0, min(14.0, val)), 2)

    # Rainfall (mm)
    val = extract_num("rainfall", "rain", "precipitation")
    if val is not None:
        extracted["rainfall"] = round(max(0.0, min(600.0, val)), 1)

    # Water TDS (ppm)
    val = extract_num("tds", "TDS", "water_tds")
    if val is not None:
        extracted["tds"] = round(max(0.0, min(2000.0, val)), 1)

    # Nitrogen (N)
    val = extract_num("N", "n", "nitrogen")
    if val is not None:
        extracted["N"] = round(max(0.0, min(300.0, val)), 1)

    # Phosphorus (P)
    val = extract_num("P", "p", "phosphorus")
    if val is not None:
        extracted["P"] = round(max(0.0, min(300.0, val)), 1)

    # Potassium (K)
    val = extract_num("K", "k", "potassium")
    if val is not None:
        extracted["K"] = round(max(0.0, min(300.0, val)), 1)

    # Soil Moisture (% 0 - 100)
    val = extract_num("soil_moisture", "moisture", "soil", "m")
    if val is not None:
        extracted["soil_moisture"] = round(max(0.0, min(100.0, val)), 1)

    # Raw Soil ADC (0 - 1023)
    val = extract_num("soil_raw", "raw", "adc")
    if val is not None:
        extracted["soil_raw"] = int(max(0, min(1023, int(val))))

    # Motion detected (bool)
    if "motion_detected" in payload and payload["motion_detected"] is not None:
        extracted["motion_detected"] = bool(payload["motion_detected"])
    elif "motion" in payload and payload["motion"] is not None:
        extracted["motion_detected"] = bool(payload["motion"])

    # Pump state (bool)
    if "pump_on" in payload and payload["pump_on"] is not None:
        extracted["pump_on"] = bool(payload["pump_on"])
    elif "pump" in payload and payload["pump"] is not None:
        extracted["pump_on"] = bool(payload["pump"])

    # Control mode
    if "control_mode" in payload and payload["control_mode"]:
        extracted["control_mode"] = str(payload["control_mode"]).upper()
    elif "mode" in payload and payload["mode"]:
        extracted["control_mode"] = str(payload["mode"]).upper()

    return extracted


def process_telemetry_reading(
    payload: Dict[str, Any], source: str = "mqtt", persist_db: bool = True
) -> Dict[str, Any]:
    """
    Unified telemetry processor used by both MQTT subscriber and HTTP REST endpoint.
    Updates global telemetry, metadata, and persists to SQLite database.
    """
    global latest_iot_data, iot_metadata

    cleaned = normalize_and_clamp(payload)
    if not cleaned:
        logger.warning(f"Telemetry payload contained no recognized metrics: {payload}")
        return latest_iot_data

    # Update in-memory state
    latest_iot_data.update(cleaned)

    # Update metadata
    iot_metadata["connected"] = True
    iot_metadata["last_packet_time"] = datetime.utcnow().isoformat()
    iot_metadata["source"] = source
    iot_metadata["packet_count"] += 1
    if "device_id" in payload and payload["device_id"]:
        iot_metadata["device_id"] = str(payload["device_id"])

    # Persist into database if requested
    if persist_db:
        try:
            from app.core.database import SessionLocal
            from app.models import db_models

            db = SessionLocal()
            try:
                reading = db_models.SensorReading(
                    device_id=iot_metadata.get("device_id", "esp32-node-01"),
                    temperature=latest_iot_data["temperature"],
                    humidity=latest_iot_data["humidity"],
                    ph=latest_iot_data["ph"],
                    rainfall=latest_iot_data["rainfall"],
                    n=latest_iot_data["N"],
                    p=latest_iot_data["P"],
                    k=latest_iot_data["K"],
                    tds=latest_iot_data.get("tds", 150.0),
                    soil_moisture=latest_iot_data.get("soil_moisture", 48.0),
                    soil_raw=int(latest_iot_data.get("soil_raw", 490)),
                    motion_detected=bool(latest_iot_data.get("motion_detected", False)),
                    pump_on=bool(latest_iot_data.get("pump_on", False)),
                    control_mode=str(latest_iot_data.get("control_mode", "AUTO")),
                )
                db.add(reading)
                db.commit()
            finally:
                db.close()
        except Exception as db_err:
            logger.error(f"Failed to persist IoT reading to DB: {db_err}")

    return latest_iot_data


def on_connect(client, userdata, flags, reason_code=None, properties=None):
    try:
        topic = iot_metadata["topic"]
        client.subscribe(topic)
        client.subscribe("agritech/sensors/#")
        iot_metadata["connected"] = True
        logger.info(f"MQTT Connected to broker and subscribed to: {topic}")
    except Exception as e:
        logger.error(f"MQTT subscribe error: {e}")


def on_disconnect(client, userdata, rc=0, *args):
    logger.warning(f"MQTT disconnected with return code: {rc}")
    iot_metadata["connected"] = False


def on_mqtt_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode("utf-8", errors="ignore")
        payload = json.loads(raw_payload)
        if isinstance(payload, dict):
            process_telemetry_reading(payload, source="mqtt", persist_db=True)
            logger.info(f"MQTT packet processed on {msg.topic}: {payload}")
        else:
            logger.warning(f"Ignored non-dict MQTT payload: {payload}")
    except Exception as e:
        logger.error(f"Error parsing MQTT message: {e}")


def start_mqtt():
    """
    Connect to HiveMQ public broker and loop forever.
    """
    global _mqtt_client
    if mqtt is None:
        logger.warning("paho-mqtt is not installed; MQTT background listener disabled.")
        return
    try:
        # Compatible with paho-mqtt v1 and v2
        try:
            client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id="agritech_node_listener",
            )
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id="agritech_node_listener")

        _mqtt_client = client
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_mqtt_message

        # Keepalive 60 seconds
        client.connect("broker.hivemq.com", 1883, 60)
        client.loop_forever()
    except Exception as e:
        logger.error(f"MQTT connection failed (running without MQTT): {e}")


def start_mqtt_background():
    """
    Thread-safe invocation to launch the MQTT daemon in a background thread if not already running.
    """
    global _mqtt_thread_started
    with _mqtt_lock:
        if not _mqtt_thread_started:
            thread = threading.Thread(target=start_mqtt, daemon=True, name="MQTT-Daemon")
            thread.start()
            _mqtt_thread_started = True
            logger.info("MQTT background daemon thread started.")
