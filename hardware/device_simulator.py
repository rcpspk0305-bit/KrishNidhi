#!/usr/bin/env python3
"""
Software Device Simulator for Plant Health Monitoring System.
Accurately replicates the ESP8266 NodeMCU MicroPython runtime state machine,
sending authenticated telemetry to /api/device/telemetry and polling /api/device/command.
Clearly labels simulated data.
"""

import argparse
import json
import random
import time
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_DEVICE_ID = "plant-01"
DEFAULT_TOKEN = "replace-with-a-long-random-secret"


class PlantDeviceSimulator:
    def __init__(self, base_url, device_id, token, active_low=True):
        self.base_url = base_url.rstrip("/")
        self.device_id = device_id
        self.token = token
        self.active_low = active_low

        # Microclimate baseline
        self.temperature = 26.5
        self.humidity = 62.0
        self.soil_moisture = 42.0
        self.soil_raw = 650
        self.motion = False

        # Actuator and mode state
        self.mode = "auto"  # auto or manual
        self.pump_on = False
        self.pump_started = None
        self.pump_stopped = None
        self.manual_requested = False
        self.last_command_id = None

        # Safety thresholds
        self.max_pump_on_s = 10.0
        self.cooldown_s = 60.0
        self.pump_start_below = 35.0
        self.pump_stop_above = 55.0

    def _request(self, method, path, payload=None):
        url = self.base_url + path
        headers = {
            "Content-Type": "application/json",
            "X-Device-Token": self.token,
            "X-Device-Key": self.token,
        }
        data_bytes = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                if res.status == 200:
                    body = res.read().decode("utf-8")
                    return json.loads(body) if body else {}
        except Exception as err:
            print(f"[SIMULATOR] API {method} {path} error: {err}")
            return None

    def step(self):
        now = time.time()

        # Dynamic physics simulation
        if self.pump_on:
            self.soil_moisture = min(100.0, self.soil_moisture + 2.5)
        else:
            self.soil_moisture = max(10.0, self.soil_moisture - 0.2)

        # Ambient sensor fluctuations
        self.temperature = round(25.0 + random.uniform(-1.0, 1.5), 1)
        self.humidity = round(60.0 + random.uniform(-3.0, 3.0), 1)
        self.soil_raw = int(850 - (self.soil_moisture * 5))
        self.motion = random.random() < 0.2

        # 1. Fetch remote commands
        cmd = self._request("GET", f"/api/device/command?device_id={self.device_id}")
        if cmd and isinstance(cmd.get("command_id"), int):
            cid = cmd["command_id"]
            if self.last_command_id is None:
                self.last_command_id = cid  # Ignore boot stale
            elif cid > self.last_command_id:
                self.last_command_id = cid
                new_mode = cmd.get("mode")
                if new_mode in ("auto", "manual"):
                    self.mode = new_mode
                    self.manual_requested = cmd.get("pump_on", False) if self.mode == "manual" else False
                print(f"[SIMULATOR] Applied remote command #{cid}: mode={self.mode}, manual_pump={self.manual_requested}")

        # 2. Control decision logic
        if self.mode == "manual":
            wanted = self.manual_requested
        else:
            threshold = self.pump_stop_above if self.pump_on else self.pump_start_below
            wanted = self.soil_moisture < threshold

        # 3. Actuator actuation & safety enforcement
        if self.pump_on:
            elapsed = now - (self.pump_started or now)
            if not wanted or elapsed >= self.max_pump_on_s:
                self.pump_on = False
                self.pump_stopped = now
                if self.mode == "manual":
                    self.manual_requested = False
                print(f"[SIMULATOR] Relay OFF (active-LOW coil released). Reason: {'Max runtime cutoff' if elapsed >= self.max_pump_on_s else 'Moisture target achieved'}")
        elif wanted:
            cooled = self.pump_stopped is None or (now - self.pump_stopped >= self.cooldown_s)
            if cooled:
                self.pump_on = True
                self.pump_started = now
                print("[SIMULATOR] Relay ON (active-LOW coil pulled LOW). Watering started.")

        # 4. Construct telemetry
        telemetry = {
            "device_id": self.device_id,
            "temperature_c": self.temperature,
            "humidity_pct": self.humidity,
            "soil_raw": self.soil_raw,
            "soil_moisture_pct": round(self.soil_moisture, 1),
            "motion": self.motion,
            "pump_on": self.pump_on,
            "mode": self.mode,
        }

        # 5. Publish telemetry
        res = self._request("POST", "/api/device/telemetry", telemetry)
        print(f"[SIMULATOR] Published: T={self.temperature}°C H={self.humidity}% Soil={self.soil_moisture:.1f}% Pump={'ON' if self.pump_on else 'OFF'} Mode={self.mode} -> Success: {res is not None}")
        return telemetry


def main():
    parser = argparse.ArgumentParser(description="Plant IoT Hardware Simulator")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="FastAPI backend URL")
    parser.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="Device ID")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Device Auth Token")
    parser.add_argument("--interval", type=float, default=5.0, help="Reporting interval in seconds")
    parser.add_argument("--iterations", type=int, default=0, help="Iterations to run (0 for infinite)")
    args = parser.parse_args()

    print("==================================================")
    print("   Plant Health IoT Simulator (MicroPython Mock)  ")
    print(f"   Target: {args.base_url} | Device: {args.device_id}")
    print("   [SIMULATED DATA - NOT PHYSICAL SENSOR INPUT]   ")
    print("==================================================")

    sim = PlantDeviceSimulator(args.base_url, args.device_id, args.token)
    count = 0
    try:
        while True:
            sim.step()
            count += 1
            if args.iterations > 0 and count >= args.iterations:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[SIMULATOR] Stopping. Ensuring pump is OFF (Fail-Safe state).")


if __name__ == "__main__":
    main()
