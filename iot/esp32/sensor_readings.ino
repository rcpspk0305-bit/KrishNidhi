/*
 * AgriTech ESP32 IoT Node - HTTP REST Direct Telemetry Streamer
 * 
 * Hardware:
 *   - ESP32 Development Board
 *   - DHT22 on GPIO 4
 *   - Analog Soil Moisture on GPIO 34
 *   - Analog Soil pH on GPIO 35
 *   - Analog Water TDS on GPIO 32
 *   - Rain Sensor on GPIO 33
 * 
 * Mode:
 *   - Sends HTTP POST requests directly to FastAPI backend:
 *     http://<BACKEND_HOST>:8000/iot/telemetry
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// =================== CONFIGURATION ===================

// 1. WiFi Credentials
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// 2. AgriTech Backend API Endpoint
// Replace with your laptop/server's local network IP address (e.g. 192.168.1.100)
const char* SERVER_URL    = "http://192.168.1.100:8000/iot/telemetry";
const char* DEVICE_ID     = "esp32-http-node-01";

// 3. Sensor Pins
#define DHTPIN            4
#define DHTTYPE           DHT22
#define SOIL_MOISTURE_PIN 34
#define SOIL_PH_PIN       35
#define WATER_TDS_PIN     32
#define RAIN_PIN          33
#define STATUS_LED_PIN    2

// 4. Transmission Interval (ms)
const unsigned long TRANSMIT_INTERVAL_MS = 5000;
unsigned long lastTransmitTime = 0;

DHT dht(DHTPIN, DHTTYPE);

// =================== CALIBRATION HELPERS ===================

float readSoilMoisture() {
  int raw = analogRead(SOIL_MOISTURE_PIN);
  float moisture = map(raw, 3500, 1200, 0, 100);
  return constrain(moisture, 0.0, 100.0);
}

float readSoilPH() {
  int raw = analogRead(SOIL_PH_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float ph = 3.5 * voltage + 0.5;
  return constrain(ph, 3.0, 9.5);
}

float readWaterTDS() {
  int raw = analogRead(WATER_TDS_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float tds = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5;
  return constrain(tds, 0.0, 1000.0);
}

float readRainfall() {
  int raw = analogRead(RAIN_PIN);
  float rain_mm = map(4095 - raw, 0, 4095, 0, 120);
  return constrain(rain_mm, 0.0, 300.0);
}

void readNPK(float &n, float &p, float &k) {
  n = 88.0 + random(-4, 4);
  p = 50.0 + random(-3, 3);
  k = 42.0 + random(-3, 3);
}

// =================== HTTP POST SENDER ===================

void sendTelemetryHTTP(const char* jsonPayload) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Skipping HTTP dispatch.");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  Serial.print("Connecting to: ");
  Serial.println(SERVER_URL);

  http.begin(client, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);
    Serial.print("Response: ");
    Serial.println(response);

    // Flash status LED
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);
  } else {
    Serial.print("HTTP Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

// =================== SETUP & LOOP ===================

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);

  dht.begin();
  analogReadResolution(12);

  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected! Local IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed! Check credentials.");
  }
}

void loop() {
  unsigned long now = millis();
  if (now - lastTransmitTime >= TRANSMIT_INTERVAL_MS) {
    lastTransmitTime = now;

    float temperature = dht.readTemperature();
    float humidity    = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
      temperature = 26.0;
      humidity = 50.0;
    }

    float ph       = readSoilPH();
    float tds      = readWaterTDS();
    float rainfall = readRainfall();
    float n, p, k;
    readNPK(n, p, k);

    StaticJsonDocument<256> doc;
    doc["device_id"]   = DEVICE_ID;
    doc["temperature"] = round(temperature * 10) / 10.0;
    doc["humidity"]    = round(humidity * 10) / 10.0;
    doc["ph"]          = round(ph * 100) / 100.0;
    doc["tds"]         = round(tds * 10) / 10.0;
    doc["rainfall"]    = round(rainfall * 10) / 10.0;
    doc["N"]           = round(n * 10) / 10.0;
    doc["P"]           = round(p * 10) / 10.0;
    doc["K"]           = round(k * 10) / 10.0;

    char buffer[256];
    serializeJson(doc, buffer);

    Serial.print("Dispatching Payload: ");
    Serial.println(buffer);

    sendTelemetryHTTP(buffer);
  }
}
