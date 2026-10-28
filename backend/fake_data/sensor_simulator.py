"""
AgriTech Real-World IoT Hardware Simulator

Simulates real-world IoT microcontrollers (ESP32/Arduino) streaming live agricultural
telemetry to the AgriTech platform via either HTTP REST POST or MQTT.

Usage:
    python backend/fake_data/sensor_simulator.py --mode http
    python backend/fake_data/sensor_simulator.py --mode mqtt
    python backend/fake_data/sensor_simulator.py --mode both --scenario rice
    python backend/fake_data/sensor_simulator.py --help
"""

import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

# Presets representing real-world field conditions
FIELD_SCENARIOS = {
    "dynamic": {
        "device_id": "esp32-dynamic-01",
        "temperature": 27.0,
        "humidity": 65.0,
        "ph": 6.8,
        "rainfall": 60.0,
        "tds": 150.0,
        "N": 85.0,
        "P": 50.0,
        "K": 45.0,
    },
    "rice": {
        "device_id": "esp32-wetland-rice",
        "temperature": 28.5,
        "humidity": 82.0,
        "ph": 6.4,
        "rainfall": 185.0,
        "tds": 175.0,
        "N": 92.0,
        "P": 46.0,
        "K": 40.0,
    },
    "potato": {
        "device_id": "esp32-highland-potato",
        "temperature": 18.2,
        "humidity": 62.0,
        "ph": 5.4,
        "rainfall": 75.0,
        "tds": 125.0,
        "N": 72.0,
        "P": 58.0,
        "K": 65.0,
    },
    "cotton": {
        "device_id": "esp32-arid-cotton",
        "temperature": 33.8,
        "humidity": 42.0,
        "ph": 7.3,
        "rainfall": 35.0,
        "tds": 240.0,
        "N": 68.0,
        "P": 38.0,
        "K": 58.0,
    },
    "maize": {
        "device_id": "esp32-plains-maize",
        "temperature": 26.4,
        "humidity": 66.0,
        "ph": 6.7,
        "rainfall": 92.0,
        "tds": 150.0,
        "N": 115.0,
        "P": 55.0,
        "K": 48.0,
    },
}


def clamp(val, low, high):
    return max(low, min(high, val))


def generate_jittered_reading(base: dict) -> dict:
    reading = dict(base)
    reading["temperature"] = round(clamp(reading["temperature"] + random.uniform(-0.4, 0.4), 10, 50), 1)
    reading["humidity"] = round(clamp(reading["humidity"] + random.uniform(-1.0, 1.0), 15, 99), 1)
    reading["ph"] = round(clamp(reading["ph"] + random.uniform(-0.04, 0.04), 3.5, 9.5), 2)
    reading["rainfall"] = round(clamp(reading["rainfall"] + random.uniform(-1.2, 1.2), 10, 300), 1)
    reading["tds"] = round(clamp(reading["tds"] + random.uniform(-2, 2), 50, 800), 1)
    reading["N"] = round(clamp(reading["N"] + random.uniform(-1, 1), 20, 200), 1)
    reading["P"] = round(clamp(reading["P"] + random.uniform(-1, 1), 10, 150), 1)
    reading["K"] = round(clamp(reading["K"] + random.uniform(-1, 1), 10, 200), 1)
    reading["timestamp"] = datetime.utcnow().isoformat()
    return reading


def send_http_packet(endpoint: str, payload: dict) -> bool:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = response.read().decode("utf-8")
            return response.status in (200, 201)
    except urllib.error.URLError as e:
        print(f" [HTTP Error] Could not connect to {endpoint}: {e.reason}")
        return False
    except Exception as ex:
        print(f" [HTTP Error] {ex}")
        return False


def main():
    parser = argparse.ArgumentParser(description="AgriTech Real-World IoT Hardware Stream Simulator")
    parser.add_argument(
        "--mode",
        choices=["http", "mqtt", "both"],
        default="http",
        help="Transmission protocol: 'http' (FastAPI REST), 'mqtt' (HiveMQ), or 'both'",
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8000/iot/telemetry",
        help="HTTP endpoint for REST ingestion (default: http://localhost:8000/iot/telemetry)",
    )
    parser.add_argument(
        "--broker",
        default="broker.hivemq.com",
        help="MQTT broker host (default: broker.hivemq.com)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1883,
        help="MQTT broker port (default: 1883)",
    )
    parser.add_argument(
        "--topic",
        default="agritech/ps10/sensors",
        help="MQTT topic (default: agritech/ps10/sensors)",
    )
    parser.add_argument(
        "--scenario",
        choices=list(FIELD_SCENARIOS.keys()),
        default="dynamic",
        help="Agricultural field preset: rice, potato, cotton, maize, or dynamic",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=4.0,
        help="Seconds between transmissions (default: 4.0)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of packets to send (0 = run indefinitely)",
    )

    args = parser.parse_args()

    # Optional MQTT client setup
    mqtt_client = None
    if args.mode in ("mqtt", "both"):
        try:
            import paho.mqtt.client as mqtt

            try:
                mqtt_client = mqtt.Client(
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                    client_id=f"sim-device-{random.randint(1000, 9999)}",
                )
            except (AttributeError, TypeError):
                mqtt_client = mqtt.Client(client_id=f"sim-device-{random.randint(1000, 9999)}")

            print(f"[*] Connecting to MQTT Broker: {args.broker}:{args.port} ...")
            mqtt_client.connect(args.broker, args.port, 60)
            mqtt_client.loop_start()
            print(f"[+] MQTT Connected successfully to topic '{args.topic}'")
        except Exception as e:
            print(f"[-] MQTT Initialization failed: {e}")
            if args.mode == "mqtt":
                sys.exit(1)

    base_preset = FIELD_SCENARIOS[args.scenario]
    print("=" * 65)
    print("  AgriTech Real-World IoT Hardware Stream Simulator")
    print(f"  Mode:       {args.mode.upper()}")
    print(f"  Scenario:   {args.scenario.upper()} Field")
    print(f"  Device ID:  {base_preset['device_id']}")
    print(f"  Interval:   {args.interval}s")
    if args.mode in ("http", "both"):
        print(f"  HTTP Target: {args.endpoint}")
    if args.mode in ("mqtt", "both"):
        print(f"  MQTT Target: {args.broker}:{args.port} [{args.topic}]")
    print("=" * 65)
    print("Streaming live telemetry (Press Ctrl+C to stop)...")

    sent_count = 0
    current_reading = dict(base_preset)

    try:
        while True:
            current_reading = generate_jittered_reading(current_reading)
            sent_count += 1
            payload_str = json.dumps(current_reading)

            status_notes = []

            # HTTP Dispatch
            if args.mode in ("http", "both"):
                success = send_http_packet(args.endpoint, current_reading)
                status_notes.append("HTTP: 200 OK" if success else "HTTP: FAIL")

            # MQTT Dispatch
            if args.mode in ("mqtt", "both") and mqtt_client:
                res = mqtt_client.publish(args.topic, payload_str)
                status_notes.append("MQTT: ACK" if res.rc == 0 else f"MQTT: ERR({res.rc})")

            # Log packet
            print(
                f"[{sent_count:04d}] {', '.join(status_notes)} | "
                f"Temp: {current_reading['temperature']}°C | "
                f"Humidity: {current_reading['humidity']}% | "
                f"pH: {current_reading['ph']} | "
                f"N-P-K: {current_reading['N']}-{current_reading['P']}-{current_reading['K']}"
            )

            if args.count > 0 and sent_count >= args.count:
                print(f"[+] Reached requested transmission count of {args.count}. Completed.")
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[*] Telemetry transmission paused by user.")
    finally:
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("[*] MQTT connection disconnected gracefully.")


if __name__ == "__main__":
    main()
