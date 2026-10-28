# ESP8266 NodeMCU Firmware - Smart Plant Monitoring & Irrigation

This directory contains the production-quality Arduino C++ firmware for the **ESP8266 NodeMCU ESP-12E** microcontroller.

---

## Hardware Pinout Mapping

| Component Pin | NodeMCU Pin | GPIO | Operating Voltage | Function |
|---|---|---|---|---|
| **DHT11 DATA** | **D6** | `GPIO 12` | 3.3V / 5V | Temperature & Relative Humidity 1-Wire |
| **PIR OUT** | **D7** | `GPIO 13` | 3.3V / 5V | Motion / Presence detection (Digital) |
| **Soil Moisture AO** | **A0** | `ADC 0` | 3.3V | Analog soil conductivity (0–1023) |
| **5V Relay IN** | **D5** | `GPIO 14` | 3.3V Logic / 5V VCC | 5V DC Submersible Pump Control |
| **LCD SDA** | **D2** | `GPIO 4` | 3.3V / 5V | I2C Data line for 16x2 Display |
| **LCD SCL** | **D1** | `GPIO 5` | 3.3V / 5V | I2C Clock line for 16x2 Display |
| **Tactile Button** | **D0** | `GPIO 16` | 3.3V (Internal pull-up) | Local pump toggle & Mode selection |

---

## Power Supply Architecture & Battery Safety

1. **Battery Pack**: Two 18650 Li-ion cells in series yield 7.4V nominal (8.4V fully charged).
2. **Voltage Regulator**: Connect the 7.4V battery pack to an **LM2596 or MP1584 Buck Converter** stepped down to **5.0V regulated**.
3. **5V Rail**: Feeds the NodeMCU `VIN` pin, the 5V Relay VCC, the 5V DC Pump (through Relay COM/NO), and the 16x2 LCD VCC.
4. **Common Ground**: All GND pins (Battery, Buck Converter, ESP8266, Relay, Sensors, Pump) **MUST be connected together**.

> [!WARNING]
> Never connect 7.4V battery voltage directly to the ESP8266 3.3V pin or to 5V sensor rails. Always verify output voltage on your buck converter with a digital multimeter before wiring to microelectronics.

---

## Required Arduino IDE Libraries

Install the following libraries via the Arduino IDE Library Manager (**Sketch -> Include Library -> Manage Libraries...**):

1. **ESP8266 Board Core**:
   - URL: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
   - Board: **NodeMCU 1.0 (ESP-12E Module)**
2. **DHT sensor library** (by Adafruit) + **Adafruit Unified Sensor**
3. **ArduinoJson** (by Benoit Blanchon, v6 or v7)
4. **LiquidCrystal_I2C** (by Frank de Brabander or Marco Schwartz)

---

## Flashing Instructions

1. Open `firmware/smart_plant/smart_plant.ino` in Arduino IDE.
2. In `config.h`, set your local Wi-Fi SSID, Wi-Fi password, and backend server IP:
   ```cpp
   #define WIFI_DEFAULT_SSID "Your_WiFi_SSID"
   #define WIFI_DEFAULT_PASS "Your_WiFi_Password"
   #define SERVER_BASE_URL   "http://192.168.1.100:8000/api/v1"
   ```
3. Connect your ESP8266 NodeMCU to your computer via micro-USB.
4. Select Port: **COMx** (Windows) or `/dev/ttyUSB0` (Linux/Mac).
5. Set Upload Speed: **115200** (or 921600 for faster flashing).
6. Click **Upload** (`Ctrl + U`).
7. Open Serial Monitor (`Ctrl + Shift + M`) set to **115200 baud** to observe boot diagnostics.

---

## Soil Sensor Calibration

Different soils have different baseline resistance and capacitance. Follow this quick calibration step:
1. Hold the sensor dry in air: Observe raw ADC printed to Serial Monitor (typically ~`800–900`). Enter this in `config.h` as `SOIL_ADC_DRY`.
2. Dip the sensor probe up to the line into water: Observe raw ADC (typically ~`350–450`). Enter this in `config.h` as `SOIL_ADC_WET`.
3. The firmware will now output a calibrated, non-linear moisture percentage strictly bounded between 0% and 100%.

---

## Physical Controls & Safety Fail-Safes

- **Button Short Press (< 2s)**: In `MANUAL` mode, immediately toggles the pump ON/OFF. In `AUTO`/`OFF` mode, switches to `MANUAL`.
- **Button Long Press (> 2.5s)**: Cycles system mode between `AUTO -> MANUAL -> OFF -> AUTO`.
- **Continuous Runtime Watchdog**: Automatically shuts the pump OFF after **15 seconds** of continuous operation to avoid flooding or pump burnout.
- **Minimum Cooldown**: Requires at least **60 seconds** between watering bursts to allow water infiltration into root soil.
- **Fail-safe Booting**: Relay output pin is written to safe inactive state *before* GPIO pin configuration to eliminate spurious startup relay pulses.
