#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include <DHT.h>
#include "config.h"

// Initialize DHT sensor (DHT11 on PIN_DHT)
static DHT dht(PIN_DHT, DHT11);

struct SensorReadings {
    float temperature;       // °C
    float humidity;          // %
    float soilMoisturePct;   // 0.0 - 100.0%
    int rawSoilADC;          // 0 - 1023
    bool motionDetected;     // true if PIR active
    bool dhtValid;           // true if DHT read was successful
    bool soilValid;          // true if soil sensor read was plausible
    bool sensorFault;        // true if any sensor is disconnected or out-of-bounds
};

static SensorReadings currentSensors = {
    0.0f, 0.0f, 0.0f, 0, false, false, false, false
};

inline void initSensors() {
    dht.begin();
    pinMode(PIN_PIR, INPUT);
    pinMode(PIN_SOIL_ANALOG, INPUT);
    Serial.println(F("[Sensors] DHT11 and PIR initialized."));
}

inline void readDHTSensor() {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t) || t < -20.0f || t > 70.0f || h < 0.0f || h > 100.0f) {
        currentSensors.dhtValid = false;
        Serial.println(F("[Sensors] WARNING: DHT11 reading invalid or sensor disconnected!"));
    } else {
        currentSensors.temperature = t;
        currentSensors.humidity = h;
        currentSensors.dhtValid = true;
    }
}

inline void readSoilMoistureSensor() {
    // 10-sample moving average to filter out switching noise and ADC jitter
    long sum = 0;
    const int SAMPLES = 10;
    for (int i = 0; i < SAMPLES; i++) {
        sum += analogRead(PIN_SOIL_ANALOG);
        delayMicroseconds(200);
    }
    int rawADC = sum / SAMPLES;
    currentSensors.rawSoilADC = rawADC;

    // Detect open circuit or short circuit faults
    if (rawADC < 30 || rawADC > 1020) {
        currentSensors.soilValid = false;
        Serial.printf("[Sensors] WARNING: Soil ADC out of electrical range: %d\n", rawADC);
    } else {
        currentSensors.soilValid = true;
    }

    // Map calibrated ADC value to moisture percentage
    // Dry ADC corresponds to 0%, Wet ADC corresponds to 100%
    float pct;
    if (SOIL_ADC_DRY != SOIL_ADC_WET) {
        pct = ((float)(SOIL_ADC_DRY - rawADC) / (float)(SOIL_ADC_DRY - SOIL_ADC_WET)) * 100.0f;
    } else {
        pct = 50.0f;
    }

    // Strict clamping to 0.0% - 100.0%
    if (pct < 0.0f) pct = 0.0f;
    if (pct > 100.0f) pct = 100.0f;

    currentSensors.soilMoisturePct = pct;
}

inline void readPIRSensor() {
    currentSensors.motionDetected = (digitalRead(PIN_PIR) == HIGH);
}

inline void updateSensorFaultStatus() {
    currentSensors.sensorFault = (!currentSensors.dhtValid || !currentSensors.soilValid);
}

#endif // SENSORS_H
