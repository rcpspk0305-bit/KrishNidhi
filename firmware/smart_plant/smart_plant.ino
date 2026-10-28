/*
 * ==============================================================================
 * AI-POWERED SMART PLANT MONITORING & AUTOMATED IRRIGATION FIRMWARE
 * Target Hardware: ESP8266 NodeMCU ESP-12E
 * Sensors: DHT11 (Temp/Hum), Capacitive/Resistive Soil Moisture (A0), PIR (D7)
 * Actuators: 5V DC Water Pump via 5V Relay (D5)
 * Display: 16x2 I2C LCD (D2/D1)
 * Controls: Tactile Push Button (D0)
 * ==============================================================================
 */

#include <Arduino.h>
#include "config.h"
#include "sensors.h"
#include "pump_control.h"
#include "display.h"
#include "network.h"

// Non-blocking timer timestamps
static unsigned long timerLastDHT = 0;
static unsigned long timerLastSoil = 0;
static unsigned long timerLastTelemetry = 0;
static unsigned long timerLastCommandPoll = 0;

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("AI-Powered Smart Plant Monitoring System starting..."));
    Serial.println(F("=================================================="));

    // 1. Initialize Relay and Pump in authoritative FAIL-SAFE OFF state
    initPumpControl();

    // 2. Initialize Environmental Sensors
    initSensors();

    // 3. Initialize 16x2 I2C Display
    initDisplay();

    // 4. Connect to Wi-Fi
    initNetwork();

    // Take initial sensor readings
    readDHTSensor();
    readSoilMoistureSensor();
    readPIRSensor();
    updateSensorFaultStatus();

    Serial.println(F("[System] Setup complete. Entering non-blocking operational loop."));
}

void loop() {
    unsigned long currentMillis = millis();

    // 1. Continuous Safety & Hardware Checks
    updatePushButton();        // Debounced button check & mode toggle
    readPIRSensor();           // Fast motion pin check
    updatePumpSafetyLoop();    // Enforces 15s max runtime, cooldown, and AUTO watering

    // 2. Periodic DHT11 Sensor Reading (every 2.5s)
    if (currentMillis - timerLastDHT >= INTERVAL_DHT_MS) {
        timerLastDHT = currentMillis;
        readDHTSensor();
        updateSensorFaultStatus();
    }

    // 3. Periodic Soil Moisture ADC Sampling (every 5.0s)
    if (currentMillis - timerLastSoil >= INTERVAL_SOIL_MS) {
        timerLastSoil = currentMillis;
        readSoilMoistureSensor();
        updateSensorFaultStatus();
    }

    // 4. Rotate 16x2 LCD Information Screens (every 3.0s)
    updateDisplayLoop();

    // 5. Manage Wi-Fi Connection State
    updateWifiConnection();

    // 6. Transmit Real-Time Telemetry to FastAPI Backend (every 5.0s or immediately on state changes)
    if (requestImmediateTelemetry || (currentMillis - timerLastTelemetry >= INTERVAL_TELEMETRY_MS)) {
        timerLastTelemetry = currentMillis;
        requestImmediateTelemetry = false;
        sendTelemetry();
    }

    // 7. Poll Backend for Pending Operator Commands (every 2.0s)
    if (currentMillis - timerLastCommandPoll >= INTERVAL_POLL_CMD_MS) {
        timerLastCommandPoll = currentMillis;
        pollCommands();
    }

    // Yield control to background ESP8266 Wi-Fi stack
    yield();
}
