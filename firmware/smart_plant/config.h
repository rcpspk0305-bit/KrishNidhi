#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ==========================================
// 1. HARDWARE GPIO PIN MAPPING (ESP8266 ESP-12E)
// ==========================================
// DHT11 Data pin -> D6 (GPIO12)
#define PIN_DHT D6

// PIR Motion Sensor OUT -> D7 (GPIO13)
#define PIN_PIR D7

// Capacitive/Resistive Soil Moisture Analog Out -> A0 (ADC0, 0-1.0V NodeMCU with divider to 3.3V)
#define PIN_SOIL_ANALOG A0

// 5V Relay Control Pin -> D5 (GPIO14)
#define PIN_RELAY D5

// I2C 16x2 LCD Display Pins
#define PIN_LCD_SDA D2 // GPIO4
#define PIN_LCD_SCL D1 // GPIO5

// Tactile Push Button -> D0 (GPIO16, active LOW with internal pull-up / external pull-up)
#define PIN_BUTTON D0

// ==========================================
// 2. RELAY & PUMP SAFETY POLARITY
// ==========================================
// Most optocoupler-isolated 5V relay modules are active-LOW:
// LOW = Relay ENERGIZED (Pump ON)
// HIGH = Relay DE-ENERGIZED (Pump OFF)
#define RELAY_ACTIVE_LEVEL LOW
#define RELAY_INACTIVE_LEVEL (!RELAY_ACTIVE_LEVEL)

// ==========================================
// 3. SOIL MOISTURE CALIBRATION CONSTANTS
// ==========================================
// Measure raw ADC in completely dry air vs submerged in water cup
#define SOIL_ADC_DRY 850   // 0% moisture benchmark
#define SOIL_ADC_WET 380   // 100% moisture benchmark

// ==========================================
// 4. AUTOMATED IRRIGATION THRESHOLDS (AUTO MODE)
// ==========================================
#define AUTO_IRRIGATION_START_PCT 30.0f // Trigger watering when moisture drops below this %
#define AUTO_IRRIGATION_STOP_PCT  55.0f // Cut off watering once moisture reaches this %

// ==========================================
// 5. HARDWARE PROTECTION TIMERS (FAIL-SAFES)
// ==========================================
// Maximum continuous pump runtime in milliseconds (prevents overflow & dry-run burnout)
#define MAX_PUMP_RUNTIME_MS 15000UL // 15 seconds max continuous run

// Minimum cooldown duration between watering events in milliseconds (allows soil absorption)
#define MIN_PUMP_COOLDOWN_MS 60000UL // 60 seconds minimum rest

// Physical push button debounce time in milliseconds
#define BUTTON_DEBOUNCE_MS 25UL

// ==========================================
// 6. WI-FI & SERVER REST CONFIGURATION
// ==========================================
// Change to your local Wi-Fi router credentials
#define WIFI_DEFAULT_SSID "Your_WiFi_SSID"
#define WIFI_DEFAULT_PASS "Your_WiFi_Password"

// FastAPI Backend URL (Update IP to your computer's LAN IP when running locally)
#define SERVER_BASE_URL "http://192.168.1.100:8000/api/v1"

// Device Credentials for Per-Device Authentication
#define DEVICE_ID "esp8266-plant-01"
#define DEVICE_API_KEY "default_secret_key_123"

// ==========================================
// 7. TASK SCHEDULING INTERVALS (MILLIS)
// ==========================================
#define INTERVAL_DHT_MS       2500UL // Read DHT11 every 2.5s
#define INTERVAL_SOIL_MS      5000UL // Read Soil moisture every 5s
#define INTERVAL_TELEMETRY_MS 5000UL // Send telemetry to server every 5s
#define INTERVAL_POLL_CMD_MS  2000UL // Poll server commands every 2s
#define INTERVAL_LCD_CYCLE_MS 3000UL // Rotate 16x2 LCD screen every 3s

// 16x2 LCD I2C Address (typically 0x27 or 0x3F)
#define LCD_I2C_ADDR 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

#endif // CONFIG_H
