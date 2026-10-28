#ifndef PUMP_CONTROL_H
#define PUMP_CONTROL_H

#include <Arduino.h>
#include "config.h"
#include "sensors.h"

enum ControlMode {
    MODE_AUTO = 0,
    MODE_MANUAL = 1,
    MODE_OFF = 2
};

struct PumpState {
    ControlMode mode;
    bool isPumpOn;
    unsigned long pumpTurnedOnTime;
    unsigned long pumpTurnedOffTime;
    bool safetyLockoutActive;
    String lockoutReason;
};

static PumpState pumpState = {
    MODE_AUTO, false, 0, 0, false, ""
};

// Physical button state variables
static int lastButtonRead = HIGH;
static int stableButtonState = HIGH;
static unsigned long lastDebounceTime = 0;
static unsigned long buttonPressStartTime = 0;
static bool buttonLongPressHandled = false;

inline const char* controlModeToString(ControlMode mode) {
    switch (mode) {
        case MODE_AUTO:   return "AUTO";
        case MODE_MANUAL: return "MANUAL";
        case MODE_OFF:    return "OFF";
        default:          return "AUTO";
    }
}

inline ControlMode stringToControlMode(const String& str) {
    if (str.equalsIgnoreCase("MANUAL")) return MODE_MANUAL;
    if (str.equalsIgnoreCase("OFF"))    return MODE_OFF;
    return MODE_AUTO;
}

// Low-level relay actuation ensuring fail-safe state
inline void setPhysicalRelay(bool state) {
    if (state) {
        digitalWrite(PIN_RELAY, RELAY_ACTIVE_LEVEL);
        pumpState.isPumpOn = true;
        pumpState.pumpTurnedOnTime = millis();
        Serial.println(F("[Pump] Relay ENERGIZED -> Water Pump ON"));
    } else {
        digitalWrite(PIN_RELAY, RELAY_INACTIVE_LEVEL);
        pumpState.isPumpOn = false;
        pumpState.pumpTurnedOffTime = millis();
        Serial.println(F("[Pump] Relay DE-ENERGIZED -> Water Pump OFF"));
    }
}

inline void initPumpControl() {
    // CRITICAL HARDWARE SAFETY:
    // Write safe inactive level BEFORE configuring as OUTPUT to prevent
    // momentary spurious relay clicks during microcontroller reset.
    digitalWrite(PIN_RELAY, RELAY_INACTIVE_LEVEL);
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, RELAY_INACTIVE_LEVEL);

    pinMode(PIN_BUTTON, INPUT_PULLUP);

    pumpState.mode = MODE_AUTO;
    pumpState.isPumpOn = false;
    pumpState.safetyLockoutActive = false;
    pumpState.pumpTurnedOffTime = millis();

    Serial.println(F("[Pump] Controller initialized in safe default OFF state."));
}

// Request to set pump state safely with checks
inline bool requestSetPump(bool desiredState, const String& source) {
    unsigned long now = millis();

    if (desiredState) {
        // Enforce OFF mode lockout
        if (pumpState.mode == MODE_OFF) {
            Serial.printf("[Pump] REJECTED (%s): System is in OFF mode.\n", source.c_str());
            return false;
        }

        // Enforce sensor health lockout
        if (!currentSensors.soilValid) {
            Serial.printf("[Pump] REJECTED (%s): Soil sensor reading invalid/disconnected.\n", source.c_str());
            return false;
        }

        // Enforce cooldown interval between waterings
        if (pumpState.pumpTurnedOffTime > 0 && (now - pumpState.pumpTurnedOffTime < MIN_PUMP_COOLDOWN_MS)) {
            unsigned long waitLeft = (MIN_PUMP_COOLDOWN_MS - (now - pumpState.pumpTurnedOffTime)) / 1000UL;
            Serial.printf("[Pump] REJECTED (%s): Cooldown active. Must wait %lu more seconds.\n", source.c_str(), waitLeft);
            return false;
        }

        setPhysicalRelay(true);
        return true;
    } else {
        // Turning OFF is ALWAYS allowed immediately for safety
        setPhysicalRelay(false);
        return true;
    }
}

inline void setControlMode(ControlMode newMode) {
    pumpState.mode = newMode;
    if (newMode == MODE_OFF && pumpState.isPumpOn) {
        setPhysicalRelay(false);
    }
    Serial.printf("[Pump] Operating Mode changed to: %s\n", controlModeToString(newMode));
}

// Check safety timers and automated irrigation logic in main loop
inline void updatePumpSafetyLoop() {
    unsigned long now = millis();

    // 1. HARDWARE FAILSAFE: Continuous Runtime Watchdog
    if (pumpState.isPumpOn) {
        if (now - pumpState.pumpTurnedOnTime >= MAX_PUMP_RUNTIME_MS) {
            Serial.println(F("[Pump] SAFETY SHUTDOWN: Maximum continuous runtime reached (15s)."));
            setPhysicalRelay(false);
            pumpState.safetyLockoutActive = true;
            pumpState.lockoutReason = "Max continuous runtime exceeded";
            return;
        }
    }

    // 2. SENSOR INTEGRITY FAILSAFE
    if (pumpState.isPumpOn && !currentSensors.soilValid) {
        Serial.println(F("[Pump] SAFETY SHUTDOWN: Soil sensor fault detected while watering!"));
        setPhysicalRelay(false);
        return;
    }

    // 3. AUTOMATIC IRRIGATION LOGIC (AUTO MODE)
    if (pumpState.mode == MODE_AUTO && currentSensors.soilValid) {
        float moisture = currentSensors.soilMoisturePct;

        if (!pumpState.isPumpOn) {
            // Check if dry enough to trigger watering
            if (moisture < AUTO_IRRIGATION_START_PCT) {
                // Must respect cooldown
                if (pumpState.pumpTurnedOffTime == 0 || (now - pumpState.pumpTurnedOffTime >= MIN_PUMP_COOLDOWN_MS)) {
                    Serial.printf("[Pump] AUTO: Soil moisture (%.1f%%) < threshold (%.1f%%). Starting irrigation.\n",
                                  moisture, AUTO_IRRIGATION_START_PCT);
                    requestSetPump(true, "AUTO_TRIGGER");
                }
            }
        } else {
            // Pump is currently running - check if moisture reached target cut-off
            if (moisture >= AUTO_IRRIGATION_STOP_PCT) {
                Serial.printf("[Pump] AUTO: Target moisture reached (%.1f%% >= %.1f%%). Stopping irrigation.\n",
                              moisture, AUTO_IRRIGATION_STOP_PCT);
                setPhysicalRelay(false);
            }
        }
    }
}

// Non-blocking tactile push-button handler with debouncing and long-press detection
inline void updatePushButton() {
    int reading = digitalRead(PIN_BUTTON);
    unsigned long now = millis();

    if (reading != lastButtonRead) {
        lastDebounceTime = now;
    }

    if ((now - lastDebounceTime) > BUTTON_DEBOUNCE_MS) {
        if (reading != stableButtonState) {
            stableButtonState = reading;

            // Button pressed down (active LOW)
            if (stableButtonState == LOW) {
                buttonPressStartTime = now;
                buttonLongPressHandled = false;
            } else {
                // Button released
                unsigned long pressDuration = now - buttonPressStartTime;
                if (!buttonLongPressHandled && pressDuration < 2000UL) {
                    // Short press: In MANUAL mode, toggle pump ON/OFF
                    Serial.println(F("[Button] Short press detected."));
                    if (pumpState.mode == MODE_MANUAL) {
                        requestSetPump(!pumpState.isPumpOn, "LOCAL_BUTTON");
                    } else {
                        Serial.println(F("[Button] In AUTO/OFF mode. Switching to MANUAL mode."));
                        setControlMode(MODE_MANUAL);
                    }
                }
            }
        } else if (stableButtonState == LOW && !buttonLongPressHandled) {
            // Check for long press (>= 2.5 seconds): Cycle modes (AUTO -> MANUAL -> OFF -> AUTO)
            if (now - buttonPressStartTime >= 2500UL) {
                buttonLongPressHandled = true;
                ControlMode nextMode = (ControlMode)(((int)pumpState.mode + 1) % 3);
                Serial.printf("[Button] Long press (2.5s) detected! Cycling mode to: %s\n",
                              controlModeToString(nextMode));
                setControlMode(nextMode);
            }
        }
    }

    lastButtonRead = reading;
}

#endif // PUMP_CONTROL_H
