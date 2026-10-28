#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "config.h"
#include "sensors.h"
#include "pump_control.h"

// Initialize 16x2 I2C LCD
static LiquidCrystal_I2C lcd(LCD_I2C_ADDR, LCD_COLS, LCD_ROWS);

static int currentLcdScreen = 0;
static unsigned long lastLcdSwitchTime = 0;
static bool isLcdAvailable = false;
static bool isWifiConnectedState = false;
static bool isServerOnlineState = false;

inline void initDisplay() {
    Wire.begin(PIN_LCD_SDA, PIN_LCD_SCL);

    // Test I2C communication
    Wire.beginTransmission(LCD_I2C_ADDR);
    if (Wire.endTransmission() == 0) {
        lcd.init();
        lcd.backlight();
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print(F("Smart Plant IoT "));
        lcd.setCursor(0, 1);
        lcd.print(F("Booting up...   "));
        isLcdAvailable = true;
        Serial.println(F("[Display] 16x2 LCD initialized at I2C 0x27."));
    } else {
        isLcdAvailable = false;
        Serial.println(F("[Display] WARNING: LCD not found at I2C address 0x27. Trying 0x3F..."));
        Wire.beginTransmission(0x3F);
        if (Wire.endTransmission() == 0) {
            LiquidCrystal_I2C altLcd(0x3F, LCD_COLS, LCD_ROWS);
            altLcd.init();
            altLcd.backlight();
            altLcd.print(F("Smart Plant IoT"));
            isLcdAvailable = true;
        }
    }
}

inline void setDisplayNetworkStatus(bool wifiConnected, bool serverOnline) {
    isWifiConnectedState = wifiConnected;
    isServerOnlineState = serverOnline;
}

// Writes exactly 16 characters padded with spaces to prevent ghost artifacts
inline void printLcdLine(uint8_t row, const String& text) {
    if (!isLcdAvailable) return;
    char buffer[17];
    snprintf(buffer, sizeof(buffer), "%-16.16s", text.c_str());
    lcd.setCursor(0, row);
    lcd.print(buffer);
}

inline void updateDisplayLoop() {
    if (!isLcdAvailable) return;

    unsigned long now = millis();
    if (now - lastLcdSwitchTime >= INTERVAL_LCD_CYCLE_MS) {
        lastLcdSwitchTime = now;
        currentLcdScreen = (currentLcdScreen + 1) % 4;

        char line1[17];
        char line2[17];

        switch (currentLcdScreen) {
            case 0:
                // Screen 1: Temp & Humidity
                if (currentSensors.dhtValid) {
                    snprintf(line1, sizeof(line1), "Temp: %.1f C", currentSensors.temperature);
                    snprintf(line2, sizeof(line2), "Humidity: %.0f%%", currentSensors.humidity);
                } else {
                    snprintf(line1, sizeof(line1), "Temp: Sensor Err");
                    snprintf(line2, sizeof(line2), "Humidity: -- %% ");
                }
                break;

            case 1:
                // Screen 2: Soil Moisture & Pump
                if (currentSensors.soilValid) {
                    snprintf(line1, sizeof(line1), "Soil: %.0f%%", currentSensors.soilMoisturePct);
                } else {
                    snprintf(line1, sizeof(line1), "Soil: Fault/Err ");
                }
                snprintf(line2, sizeof(line2), "Pump: %s", pumpState.isPumpOn ? "ON " : "OFF");
                break;

            case 2:
                // Screen 3: WiFi & Server Status
                snprintf(line1, sizeof(line1), "WiFi: %s", isWifiConnectedState ? "Connected" : "Offline  ");
                snprintf(line2, sizeof(line2), "Server: %s", isServerOnlineState ? "Online   " : "Offline  ");
                break;

            case 3:
                // Screen 4: PIR Motion & Mode
                snprintf(line1, sizeof(line1), "Motion: %s", currentSensors.motionDetected ? "Yes" : "No ");
                snprintf(line2, sizeof(line2), "Mode: %s", controlModeToString(pumpState.mode));
                break;
        }

        printLcdLine(0, line1);
        printLcdLine(1, line2);
    }
}

#endif // DISPLAY_H
