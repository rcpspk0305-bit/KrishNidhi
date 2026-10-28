#ifndef NETWORK_H
#define NETWORK_H

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors.h"
#include "pump_control.h"
#include "display.h"

static WiFiClient wifiClient;
static unsigned long lastWifiReconnectAttempt = 0;
static bool lastServerSuccess = false;

inline void initNetwork() {
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    Serial.printf("[Network] Connecting to Wi-Fi SSID: %s\n", WIFI_DEFAULT_SSID);
    WiFi.begin(WIFI_DEFAULT_SSID, WIFI_DEFAULT_PASS);
}

inline void updateWifiConnection() {
    unsigned long now = millis();
    if (WiFi.status() != WL_CONNECTED) {
        setDisplayNetworkStatus(false, false);
        if (now - lastWifiReconnectAttempt > 10000UL) {
            lastWifiReconnectAttempt = now;
            Serial.println(F("[Network] Reconnecting to Wi-Fi..."));
            WiFi.disconnect();
            WiFi.begin(WIFI_DEFAULT_SSID, WIFI_DEFAULT_PASS);
        }
    } else {
        setDisplayNetworkStatus(true, lastServerSuccess);
    }
}

// -------------------------------------------------------------
// 1. SEND TELEMETRY
// POST /api/v1/devices/{id}/telemetry
// -------------------------------------------------------------
inline bool sendTelemetry() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println(F("[Network] Telemetry skipped: Wi-Fi offline."));
        return false;
    }

    HTTPClient http;
    String url = String(SERVER_BASE_URL) + "/devices/" + String(DEVICE_ID) + "/telemetry";

    if (!http.begin(wifiClient, url)) {
        Serial.println(F("[Network] HTTP begin failed for telemetry"));
        return false;
    }

    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Key", DEVICE_API_KEY);
    http.setTimeout(4000);

    // Build JSON payload using ArduinoJson
    StaticJsonDocument<256> doc;
    if (currentSensors.dhtValid) {
        doc["temperature"] = serialized(String(currentSensors.temperature, 1));
        doc["humidity"] = serialized(String(currentSensors.humidity, 1));
    }
    if (currentSensors.soilValid) {
        doc["soil_moisture"] = serialized(String(currentSensors.soilMoisturePct, 1));
        doc["soil_raw"] = currentSensors.rawSoilADC;
    }
    doc["motion_detected"] = currentSensors.motionDetected;
    doc["pump_on"] = pumpState.isPumpOn;
    doc["control_mode"] = controlModeToString(pumpState.mode);
    doc["uptime_seconds"] = millis() / 1000UL;

    String jsonString;
    serializeJson(doc, jsonString);

    int httpCode = http.POST(jsonString);
    bool success = false;

    if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
        Serial.println(F("[Network] Telemetry delivered successfully."));
        success = true;
        lastServerSuccess = true;
    } else {
        Serial.printf("[Network] Telemetry POST failed. Code: %d, Response: %s\n",
                      httpCode, http.getString().c_str());
        lastServerSuccess = false;
    }

    http.end();
    setDisplayNetworkStatus(true, lastServerSuccess);
    return success;
}

// -------------------------------------------------------------
// 2. ACKNOWLEDGE COMMAND
// POST /api/v1/devices/{id}/commands/{command_id}/ack
// -------------------------------------------------------------
inline void acknowledgeCommand(const String& cmdId, const String& status, bool confirmedState, const String& reason) {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = String(SERVER_BASE_URL) + "/devices/" + String(DEVICE_ID) + "/commands/" + cmdId + "/ack";

    if (!http.begin(wifiClient, url)) return;

    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Key", DEVICE_API_KEY);
    http.setTimeout(3000);

    StaticJsonDocument<200> doc;
    doc["status"] = status; // APPLIED, REJECTED, FAILED
    doc["confirmed_state"] = confirmedState;
    doc["reason"] = reason;

    String payload;
    serializeJson(doc, payload);

    int httpCode = http.POST(payload);
    Serial.printf("[Network] Command %s ACK (%s) -> HTTP %d\n", cmdId.c_str(), status.c_str(), httpCode);

    http.end();
}

// -------------------------------------------------------------
// 3. POLL COMMANDS
// GET /api/v1/devices/{id}/commands
// -------------------------------------------------------------
inline void pollCommands() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = String(SERVER_BASE_URL) + "/devices/" + String(DEVICE_ID) + "/commands";

    if (!http.begin(wifiClient, url)) return;

    http.addHeader("X-Device-Key", DEVICE_API_KEY);
    http.setTimeout(3000);

    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
        String resp = http.getString();
        StaticJsonDocument<512> doc;
        DeserializationError err = deserializeJson(doc, resp);

        if (!err && doc["has_command"] == true) {
            JsonObject cmd = doc["command"];
            String cmdId = cmd["command_id"].as<String>();
            String action = cmd["action"].as<String>();
            String valStr = cmd["value"].as<String>();

            Serial.printf("[Network] Received command: ID=%s, Action=%s, Val=%s\n",
                          cmdId.c_str(), action.c_str(), valStr.c_str());

            if (action == "SET_PUMP") {
                bool desiredOn = (valStr.equalsIgnoreCase("true") || valStr == "1");
                bool applied = requestSetPump(desiredOn, "REMOTE_COMMAND");
                if (applied) {
                    acknowledgeCommand(cmdId, "APPLIED", pumpState.isPumpOn, "Pump state transitioned successfully");
                } else {
                    acknowledgeCommand(cmdId, "REJECTED", pumpState.isPumpOn, "Command rejected by safety lockout or cooldown");
                }
            } else if (action == "SET_MODE") {
                ControlMode targetMode = stringToControlMode(valStr);
                setControlMode(targetMode);
                acknowledgeCommand(cmdId, "APPLIED", pumpState.isPumpOn, String("Mode updated to ") + valStr);
            } else {
                acknowledgeCommand(cmdId, "REJECTED", pumpState.isPumpOn, "Unknown action command");
            }
        }
    }

    http.end();
}

#endif // NETWORK_H
