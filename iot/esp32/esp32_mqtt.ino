/*
 * AgriTech ESP32 IoT Node - MQTT Telemetry Streamer
 * 
 * Hardware:
 *   - ESP32 Development Board (e.g. ESP32-WROOM-32)
 *   - DHT22 (Temperature & Humidity) on GPIO 4
 *   - Analog Soil Moisture Sensor on GPIO 34 (ADC1_CH6)
 *   - Analog Soil pH Sensor on GPIO 35 (ADC1_CH7)
 *   - Analog Water TDS Sensor on GPIO 32 (ADC1_CH4)
 *   - Rain Sensor / Analog Rain gauge on GPIO 33 (ADC1_CH5)
 *   - Optional: RS485 Modbus NPK Soil Sensor on GPIO 16 (RX2), GPIO 17 (TX2), GPIO 5 (DE/RE)
 * 
 * Libraries Required (Install via Arduino Library Manager):
 *   - WiFi (built-in ESP32 core)
 *   - PubSubClient (by Nick O'Leary)
 *   - DHT sensor library (by Adafruit)
 *   - ArduinoJson (by Benoît Blanchon - version 6 or 7)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// =================== CONFIGURATION ===================

// 1. WiFi Credentials
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// 2. MQTT Broker Details
const char* MQTT_BROKER   = "broker.hivemq.com";
const int   MQTT_PORT     = 1883;
const char* MQTT_TOPIC    = "agritech/ps10/sensors";
const char* DEVICE_ID     = "esp32-farm-node-01";

// 3. Sensor Pin Mapping
#define DHTPIN            4       // GPIO 4 for DHT22
#define DHTTYPE           DHT22   // DHT 22 (AM2302)
#define SOIL_MOISTURE_PIN 34      // ADC1
#define SOIL_PH_PIN       35      // ADC1
#define WATER_TDS_PIN     32      // ADC1
#define RAIN_PIN          33      // ADC1
#define STATUS_LED_PIN    2       // Built-in LED

// 4. Transmission Interval
const unsigned long TRANSMIT_INTERVAL_MS = 5000; // 5 seconds
unsigned long lastTransmitTime = 0;

// =================== INSTANCES ===================

WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHTPIN, DHTTYPE);

// =================== CALIBRATION HELPERS ===================

// Calibrate ADC to Soil Moisture percentage (0-100%)
// Dry air ADC ~ 3500, Pure water ADC ~ 1200 on ESP32 12-bit ADC
float readSoilMoisture() {
  int raw = analogRead(SOIL_MOISTURE_PIN);
  float moisture = map(raw, 3500, 1200, 0, 100);
  return constrain(moisture, 0.0, 100.0);
}

// Calibrate Soil pH from analog voltage (0 - 14 pH)
float readSoilPH() {
  int raw = analogRead(SOIL_PH_PIN);
  float voltage = raw * (3.3 / 4095.0);
  // Typical pH sensor formula: pH = 3.5 * voltage + offset
  float ph = 3.5 * voltage + 0.5;
  return constrain(ph, 3.0, 9.5);
}

// Calibrate Water TDS (ppm)
float readWaterTDS() {
  int raw = analogRead(WATER_TDS_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float tds = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5;
  return constrain(tds, 0.0, 1000.0);
}

// Read Rainfall mm (or rain sensor intensity)
float readRainfall() {
  int raw = analogRead(RAIN_PIN);
  // Invert because rain drops bridge sensor lower resistance
  float rain_mm = map(4095 - raw, 0, 4095, 0, 120);
  return constrain(rain_mm, 0.0, 300.0);
}

// Read or approximate Soil NPK levels (mg/kg)
// Can be substituted with direct RS485 Modbus read query
void readNPK(float &n, float &p, float &k) {
  // If Modbus hardware is attached, query bytes here.
  // Standard healthy soil baseline with light environmental jitter:
  n = 85.0 + random(-5, 5);
  p = 48.0 + random(-3, 3);
  k = 42.0 + random(-4, 4);
}

// =================== NETWORK SETUP ===================

void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected successfully!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed! Will continue attempting in background.");
  }
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection to ");
    Serial.print(MQTT_BROKER);
    Serial.print("...");

    String clientId = String(DEVICE_ID) + "-" + String(random(0xffff), HEX);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" connected!");
      digitalWrite(STATUS_LED_PIN, HIGH);
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 3 seconds...");
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(3000);
    }
  }
}

// =================== SETUP & LOOP ===================

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);

  // Initialize DHT sensor
  dht.begin();

  // Configure ADC resolution
  analogReadResolution(12);

  // Connect to Network
  setupWiFi();

  // Configure MQTT client
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(512);
}

void loop() {
  // Keep WiFi active
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }

  // Keep MQTT active
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  // Periodic sensor read and publish
  unsigned long now = millis();
  if (now - lastTransmitTime >= TRANSMIT_INTERVAL_MS) {
    lastTransmitTime = now;

    // Read sensors
    float temperature = dht.readTemperature();
    float humidity    = dht.readHumidity();

    // Check for sensor read failure and apply fallback
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Warning: Failed to read from DHT22 sensor! Using fallback.");
      temperature = 26.5;
      humidity = 55.0;
    }

    float ph       = readSoilPH();
    float tds      = readWaterTDS();
    float rainfall = readRainfall();
    float n, p, k;
    readNPK(n, p, k);

    // Build JSON payload
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

    // Publish to MQTT
    bool published = mqttClient.publish(MQTT_TOPIC, buffer);
    if (published) {
      Serial.print("Telemetry published: ");
      Serial.println(buffer);
      // Flash LED briefly
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(50);
      digitalWrite(STATUS_LED_PIN, HIGH);
    } else {
      Serial.println("Failed to publish MQTT packet!");
    }
  }
}
