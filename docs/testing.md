# Verification & Testing Guide

This document details the automated software test results, web frontend verification, and the physical hardware testing checklist for the **AI-Powered Smart Plant Monitoring System**.

---

## 1. Automated Backend Test Suite

The backend includes a comprehensive automated test suite powered by `pytest` and `httpx`.

### 1.1 Test Execution Command
From the `backend/` directory:
```bash
python -m pytest tests -v
```

### 1.2 Verification Results (Executed in Environment)
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\rc821\OneDrive\Desktop\Projects\NRCM-Codestrom\backend
plugins: anyio-4.13.0, asyncio-1.4.0, cov-7.1.0
collected 19 items

tests/test_analytics.py::test_calculate_vpd PASSED                       [  5%]
tests/test_analytics.py::test_rule_engine_low_moisture_detection PASSED  [ 10%]
tests/test_analytics.py::test_analytics_and_recommendations_api PASSED   [ 15%]
tests/test_devices.py::test_register_device PASSED                       [ 21%]
tests/test_devices.py::test_duplicate_device_registration_fails PASSED   [ 26%]
tests/test_devices.py::test_list_devices PASSED                          [ 31%]
tests/test_devices.py::test_get_device_status PASSED                     [ 36%]
tests/test_devices.py::test_update_plant_profile PASSED                  [ 42%]
tests/test_pump_control.py::test_pump_command_flow_and_ack PASSED        [ 47%]
tests/test_pump_control.py::test_command_expiration PASSED               [ 52%]
tests/test_streamlit_workflows.py::test_streamlit_app_loads_without_errors PASSED [ 57%]
tests/test_streamlit_workflows.py::test_realtime_dashboard_workflow PASSED [ 63%]
tests/test_streamlit_workflows.py::test_crop_recommendation_workflow PASSED [ 68%]
tests/test_streamlit_workflows.py::test_leaf_disease_diagnosis_workflow PASSED [ 73%]
tests/test_streamlit_workflows.py::test_ai_chatbot_workflow PASSED       [ 78%]
tests/test_telemetry.py::test_ingest_telemetry_success PASSED            [ 84%]
tests/test_telemetry.py::test_ingest_telemetry_unauthorized PASSED       [ 89%]
tests/test_telemetry.py::test_low_soil_moisture_triggers_alert PASSED    [ 94%]
tests/test_telemetry.py::test_get_telemetry_history PASSED               [100%]

======================= 19 passed in 22.67s =======================
```

### 1.3 Coverage Summary
1. **Device Security**: Verified SHA-256 salted API key hashing, duplicate registration rejections, and unauthorized telemetry 401 rejections.
2. **Telemetry Validation**: Ingestion of temperature, humidity, calibrated soil moisture percentage, raw ADC, and motion flags.
3. **Threshold Alerts**: Verification that soil moisture < 30% triggers `SOIL_DRY` alerts.
4. **Command Pipeline & Acks**: End-to-end command generation, polling by device, execution acknowledgment, state confirmation, and TTL expiration.
5. **Agronomic Rule Engine**: Accurate Vapor Pressure Deficit (VPD) computation and health index scoring.
6. **Streamlit Workflows**: End-to-end headless verification via `AppTest` for:
   - Real-time Dashboard (telemetry toggle, manual simulator, database persistence, notifications)
   - Crop Recommendation Suitability Engine (soil & weather parameter inference)
   - Leaf Disease Diagnosis (multimodal Gemini vision and agronomic action plan)
   - AI Chatbot Assistant (multilingual agricultural RAG & history clearing)

---

## 2. Frontend Build Verification

The Next.js 16 frontend build was validated using:
```bash
cd frontend
npm run build
```

**Result:**
- TypeScript strict type checking passed in 10.1s with **0 type errors**.
- All static pages and dynamic dashboard routes (`/`, `/dashboard`, `/plant-monitor`, `/scheme-finder`) generated successfully.

---

## 3. Physical Hardware Testing Checklist

The following tests require physical hardware components and must be performed on the physical test bench.

### Test 1: Power Supply & Multimeter Verification
- [ ] Connect dual 18650 battery pack to buck converter input.
- [ ] Measure buck converter output with digital multimeter. Adjust potentiometer until voltage reads exactly **5.00V ± 0.05V**.
- [ ] Verify NodeMCU `3.3V` pin outputs 3.28V–3.32V.

### Test 2: Relay Boot Polarity & Startup Failsafe
- [ ] Power on the ESP8266 while observing the 5V relay module LED.
- [ ] **Pass Condition**: The relay must **NOT** click or momentarily turn on during power-up or reset.
- [ ] **Safety Mechanism**: Verified by `initPumpControl()` writing `RELAY_INACTIVE_LEVEL` before enabling GPIO `OUTPUT`.

### Test 3: Soil Moisture Sensor Calibration
- [ ] Hold soil sensor dry in air: Verify Serial Monitor reads ~`800–900` ADC (0% moisture).
- [ ] Submerge sensor probe up to the marked line in a glass of water: Verify Serial Monitor reads ~`350–450` ADC (100% moisture).
- [ ] Verify moisture percentage clamps strictly between 0.0% and 100.0%.

### Test 4: Maximum Continuous Pump Runtime Watchdog
- [ ] Switch system to `MANUAL` mode using push button or dashboard.
- [ ] Turn the pump ON and leave it running.
- [ ] **Pass Condition**: After exactly **15 seconds**, the ESP8266 must autonomously de-energize the relay and trigger a runtime safety alert.

### Test 5: Minimum Cooldown Lockout
- [ ] Immediately after the pump shuts off, attempt to turn the pump ON again.
- [ ] **Pass Condition**: The command must be rejected with the message *"Cooldown active. Must wait X more seconds."*

### Test 6: Sensor Failure Lockout
- [ ] Disconnect the analog wire from pin `A0` while in `AUTO` mode.
- [ ] **Pass Condition**: The ESP8266 detects ADC out-of-range (<30 or >1020), flags `sensorFault`, and refuses to start the pump.

### Test 7: Wi-Fi Disconnection & Autonomous Offline Irrigation
- [ ] Disconnect your home Wi-Fi router while the ESP8266 is operating in `AUTO` mode.
- [ ] Dip the soil moisture sensor into dry soil (<30%).
- [ ] **Pass Condition**: The ESP8266 continues to monitor soil moisture locally, triggers the pump, irrigates until moisture > 55% or 15s timeout, and does not crash or block execution.
- [ ] Reconnect Wi-Fi: ESP8266 re-establishes connection and resumes uploading telemetry.

### Test 8: Physical Push Button Debounce & Mode Cycling
- [ ] Press tactile button connected to `D0` rapidly. Verify no erratic relay bouncing occurs (debounced with 25ms filter).
- [ ] Short press (<2s): In `MANUAL` mode, toggles pump ON/OFF.
- [ ] Long press (>2.5s): Verify mode cycles between `AUTO -> MANUAL -> OFF -> AUTO`.
