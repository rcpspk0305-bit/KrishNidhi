# Real-World IoT Hardware Integration Guide

This guide describes how to connect real-world IoT microcontrollers (ESP32, ESP8266, Arduino with WiFi/GSM) and sensors to the **KrishiNidhi / AgriTech** platform.

---

## 1. Architecture Overview

```
                      +-----------------------------+
                      |   Physical Field Sensors    |
                      |  (DHT22, Soil pH, Moisture, |
                      |    Water TDS, NPK Sensor)   |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     ESP32 Microcontroller   |
                      +--------------+--------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
  (Method A: MQTT Protocol)                       (Method B: HTTP REST)
             |                                               |
             v                                               v
+--------------------------+                   +---------------------------+
|   HiveMQ Public Broker   |                   |    FastAPI REST Backend   |
|   broker.hivemq.com:1883 |                   |    POST /iot/telemetry    |
|   agritech/ps10/sensors  |                   +-------------+-------------+
+------------+-------------+                                 |
             |                                               |
             +-----------------------+-----------------------+
                                     |
                                     v
                       +---------------------------+
                       |    Unified Ingestion &    |
                       |    SQLite Database Sync   |
                       +-------------+-------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
             v                                               v
+--------------------------+                   +---------------------------+
|    Streamlit Dashboard   |                   |      Next.js Frontend     |
|   (Live Hardware Sync)   |                   |      (Live Telemetry)     |
+--------------------------+                   +---------------------------+
```

---

## 2. Hardware Pinout Mapping (ESP32-WROOM-32)

| Sensor | ESP32 GPIO Pin | Type / Protocol | Operating Voltage |
| :--- | :--- | :--- | :--- |
| **DHT22** (Temp & Humidity) | `GPIO 4` | Digital (1-Wire) | 3.3V - 5V |
| **Capacitive Soil Moisture** | `GPIO 34` | Analog (ADC1_CH6) | 3.3V |
| **Analog Soil pH Probe** | `GPIO 35` | Analog (ADC1_CH7) | 5V (Signal to ADC) |
| **Analog Water TDS Meter** | `GPIO 32` | Analog (ADC1_CH4) | 3.3V - 5V |
| **Analog Rain Gauge / Plate** | `GPIO 33` | Analog (ADC1_CH5) | 3.3V |
| **Status Indicator LED** | `GPIO 2` | Digital Output | Built-in |
| **NPK RS485 (Optional)** | `GPIO 16 (RX2), 17 (TX2), 5 (DE/RE)` | UART / Modbus | 5V - 12V (MAX485) |

---

## 3. Communication Methods

### Method A: MQTT Publishing (Recommended for Remote Fields)

- **Broker**: `broker.hivemq.com`
- **Port**: `1883`
- **Topic**: `agritech/ps10/sensors`
- **Payload Format**:
  ```json
  {
    "device_id": "esp32-farm-01",
    "temperature": 27.5,
    "humidity": 64.0,
    "ph": 6.8,
    "tds": 150.0,
    "rainfall": 55.0,
    "N": 88.0,
    "P": 50.0,
    "K": 42.0
  }
  ```
- **Arduino Firmware Sketch**: Located at [`iot/esp32/esp32_mqtt.ino`](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/iot/esp32/esp32_mqtt.ino).

### Method B: HTTP REST Ingestion (Recommended for Firewalled Networks)

- **HTTP Method**: `POST`
- **Endpoint**: `http://<SERVER_IP>:8000/iot/telemetry`
- **Headers**: `Content-Type: application/json`
- **Arduino Firmware Sketch**: Located at [`iot/esp32/sensor_readings.ino`](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/iot/esp32/sensor_readings.ino).

### Method C: Node-RED Gateway Bridge

- A full Node-RED visual flow is provided at [`iot/node-red/flows.json`](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/iot/node-red/flows.json).
- Import this flow into any local Node-RED instance to bridge incoming MQTT messages directly to the FastAPI REST backend.

---

## 4. Software Setup & Firmware Upload

1. Open the **Arduino IDE** (version 2.x recommended).
2. Install the **ESP32 Board Package**:
   - `Tools` -> `Board` -> `Boards Manager` -> Search for `esp32` by Espressif Systems and click Install.
3. Install the required libraries from `Sketch` -> `Include Library` -> `Manage Libraries`:
   - `PubSubClient` (by Nick O'Leary)
   - `DHT sensor library` (by Adafruit)
   - `Adafruit Unified Sensor` (by Adafruit)
   - `ArduinoJson` (by Benoît Blanchon)
4. Open [`iot/esp32/esp32_mqtt.ino`](file:///c:/Users/rc821/OneDrive/Desktop/Projects/NRCM-Codestrom/iot/esp32/esp32_mqtt.ino).
5. Update your WiFi credentials:
   ```cpp
   const char* WIFI_SSID     = "Your_WiFi_Network";
   const char* WIFI_PASSWORD = "Your_Password";
   ```
6. Select your Board (e.g. `ESP32 Dev Module`) and COM Port, then click **Upload**.
7. Open Serial Monitor at **115200 baud** to view real-time transmission logs.

---

## 5. Instant Terminal Testing (Without Physical Hardware)

You can test real-time ingestion instantly using cURL or the Python sensor simulator:

### 1. Test via cURL (HTTP REST)
```bash
curl -X POST http://localhost:8000/iot/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-terminal-test",
    "temperature": 29.2,
    "humidity": 68.5,
    "ph": 6.7,
    "rainfall": 75.0,
    "N": 95,
    "P": 52,
    "K": 48,
    "tds": 160
  }'
```

### 2. Stream Live Telemetry with the Python Simulator
```bash
# Stream realistic Rice field conditions over HTTP
python backend/fake_data/sensor_simulator.py --mode http --scenario rice

# Stream over MQTT
python backend/fake_data/sensor_simulator.py --mode mqtt --scenario maize

# Stream to both HTTP and MQTT concurrently
python backend/fake_data/sensor_simulator.py --mode both
```

---

## 6. Real-Time Verification

1. **In Streamlit Dashboard (`http://localhost:8501`)**:
   - Navigate to **"📊 Real-time Dashboard"**.
   - Select **"🛰️ Real-World Live IoT Stream"**.
   - Notice the green badge indicating `HARDWARE LIVE & TRANSMITTING`, the device ID, packet count, and live telemetry cards updating in real time.
2. **In Next.js Frontend (`http://localhost:3000`)**:
   - The central overview window and telemetry cards update from `/dashboard/windows/overview`.
3. **In SQLite Database**:
   - All incoming readings are permanently persisted into `backend/agritech.db` under the `sensor_readings` table.
