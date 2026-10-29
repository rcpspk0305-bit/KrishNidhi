# Hardware Connections & Electrical Wiring Guide

This document specifies the exact physical wiring, power distribution, logic-level requirements, and safety protections for the **AI-Powered Smart Plant Monitoring System**.

---

## 1. Complete Pinout Interconnect Table

| Component | Pin Label | Wire Color (Recommended) | Target ESP8266 NodeMCU Pin | Voltage / Signal Spec |
|---|---|---|---|---|
| **DHT11** | VCC | Red | **3.3V** | 3.3V Regulated DC |
| **DHT11** | DATA | Yellow | **D6 (GPIO 12)** | 1-Wire Digital (Pull-up: 10kΩ to 3.3V if bare sensor) |
| **DHT11** | GND | Black | **GND** | System Ground |
| **Soil Moisture (LM393)** | VCC | Red | **3.3V** | 3.3V DC (Ensures AO stays <= 3.3V) |
| **Soil Moisture (LM393)** | AO (Analog Out) | Blue | **A0 (ADC 0)** | 0.0V – 3.3V Analog Voltage |
| **Soil Moisture (LM393)** | GND | Black | **GND** | System Ground |
| **PIR Motion Sensor** | VCC | Red | **5V (VIN / Buck Out)** | 5V DC (Onboard regulator powers PIR IC) |
| **PIR Motion Sensor** | OUT | Orange | **D7 (GPIO 13)** | 3.3V Digital High on Motion |
| **PIR Motion Sensor** | GND | Black | **GND** | System Ground |
| **1-Channel 5V Relay** | VCC | Red | **5V (VIN / Buck Out)** | 5V DC Relay Coil Power |
| **1-Channel 5V Relay** | IN | Purple | **D5 (GPIO 14)** | Active-LOW 3.3V Digital Control Signal |
| **1-Channel 5V Relay** | GND | Black | **GND** | System Ground |
| **16x2 LCD (I2C Module)** | VCC | Red | **5V (VIN / Buck Out)** | 5V DC for Display & LED Backlight |
| **16x2 LCD (I2C Module)** | GND | Black | **GND** | System Ground |
| **16x2 LCD (I2C Module)** | SDA | Green | **D2 (GPIO 4)** | I2C Serial Data (3.3V Logic) |
| **16x2 LCD (I2C Module)** | SCL | White | **D1 (GPIO 5)** | I2C Serial Clock (3.3V Logic) |
| **Tactile Push Button** | Terminal 1 | Grey | **D0 (GPIO 16)** | External 10kΩ Pull-Up to 3.3V (Active-LOW) |
| **Tactile Push Button** | Terminal 2 | Black | **GND** | System Ground Contact |
| **5V DC Water Pump (+)**| Positive Wire | Red | **Relay NO (Normally Open)** | Switched 5V Rail |

| **5V DC Water Pump (-)**| Negative Wire | Black | **GND** | Direct Ground Return |

---

## 2. Power Supply & Battery Regulation

### 2.1 Battery Specification
- **Cells**: Two 18650 Lithium-Ion rechargeable batteries connected in series.
- **Nominal Pack Voltage**: 2 × 3.7V = **7.4V**.
- **Fully Charged Voltage**: 2 × 4.2V = **8.4V**.
- **Cutoff Voltage**: 2 × 3.0V = **6.0V**.
- **Protection**: Use battery cells with an integrated Battery Management System (BMS) protection PCB to prevent over-discharge, over-charge, and short circuits.

### 2.2 Step-Down Voltage Regulator (Buck Converter)
- **Model**: LM2596 or MP1584 DC-DC Buck Converter Module.
- **Input**: 7.4V from battery pack through an ON/OFF toggle switch.
- **Output**: Calibrated using the onboard multi-turn potentiometer to **strictly 5.00V ± 0.05V**.
- **Current Rating**: Minimum 2.0A continuous (to handle NodeMCU Wi-Fi RF peaks up to 450mA + Relay coil 75mA + 5V Pump starting surge ~800mA).

> [!CAUTION]
> Always disconnect your electronics and test the output of the buck converter with a digital multimeter before wiring to NodeMCU `VIN` or sensor `5V` pins!

```text
  [ 7.4V 18650 Pack ]
          │
          ▼
   [ Power Switch ]
          │
          ▼
  [ Buck Converter ] ──(5.0V Regulated)───┬──> NodeMCU VIN Pin
  (Step-down to 5V)                       ├──> 5V Relay VCC
                                          ├──> 16x2 LCD VCC
                                          ├──> PIR Sensor VCC
                                          └──> Relay COM Pin ──[NO]──> 5V Pump (+)

  [ Common Ground ] ──────────────────────┴──> All Module GND Pins & Pump (-)
```

---

## 3. Voltage Level & Logic Compatibility

### 3.1 NodeMCU GPIO Voltage (3.3V Max)
- The ESP8266 operates strictly at **3.3V CMOS logic**. Applying 5V to any GPIO pin will permanently degrade or destroy the chip.
- **DHT11 & Soil Sensor**: Powered from the NodeMCU **3.3V** pin. This ensures their signal outputs never exceed 3.3V.
- **PIR Sensor**: Powered from 5V, but its internal voltage regulator generates an output signal at **3.3V**, making it directly safe for GPIO D7.
- **16x2 I2C Backpack**: Powered from 5V. If your I2C module has pull-ups to 5V, use a 2-channel bidirectional logic level shifter (or remove 5V pull-up resistors on the backpack) to keep D1/D2 lines at 3.3V.

### 3.2 Relay Module Active-LOW Polarity
- Most 1-channel optocoupled relay modules have an active-LOW input (`IN` pin pulled to GND engages the relay).
- When the ESP8266 reboots, floating GPIO pins could cause a momentary relay pulse if not initialized properly.
- **Firmware Safeguard**: The firmware sets pin D5 `HIGH` *before* enabling `OUTPUT` mode in `initPumpControl()`.
- **Relay COM / NO Wiring**:
  - Connect the 5V power supply to **COM** (Common).
  - Connect the Red (+) wire of the submersible pump to **NO** (Normally Open).
  - When the relay is unpowered or in reset, the circuit is open and the pump cannot run.

### 3.3 Push Button External Pull-Up (GPIO16 / D0)
- Unlike other ESP8266 GPIO pins, **GPIO16 does not have an internal pull-up resistor** in standard MicroPython.
- An **external 10kΩ pull-up resistor** must be connected between **D0 (GPIO16)** and the **3.3V** rail.
- The tactile push button connects between **D0 (GPIO16)** and **GND**.
- When the button is unpressed, the 10kΩ pull-up holds the pin solidly at 3.3V (`value() == 1`).
- When the button is depressed, the pin is pulled to GND (`value() == 0`).

---


## 4. Hardware Assembly Checklist

1. [ ] Calibrate buck converter output to 5.0V before connecting any microcontroller.
2. [ ] Tie all ground wires (Battery, Buck Converter, ESP8266, Relay, Sensors, Pump) together to a common ground bus.
3. [ ] Verify DHT11 data line is connected to **D6 (GPIO 12)**.
4. [ ] Verify PIR output is connected to **D7 (GPIO 13)**.
5. [ ] Verify Soil Moisture analog pin is connected to **A0**.
6. [ ] Verify Relay signal input is connected to **D5 (GPIO 14)**.
7. [ ] Verify LCD I2C bus: SDA to **D2**, SCL to **D1**.
8. [ ] Verify Push Button connects between **D0** and **GND**.
9. [ ] Inspect pump tubing: ensure pump outlet tube is securely inserted into planter soil with a small siphon-break hole to avoid gravity back-siphoning.
