import network
import time
import gc
import dht
import ujson
try:
    import urequests as requests
except ImportError:
    import requests


from machine import Pin, ADC
from config import *
from command_protocol import apply_command

# GPIO mappings from the finalized wiring
soil_sensor = ADC(0)  # A0
dht_sensor = dht.DHT11(Pin(12))  # D6
pir_sensor = Pin(13, Pin.IN)  # D7
button = Pin(16, Pin.IN)  # D0, external pull-up

RELAY_ON = 0 if RELAY_ACTIVE_LOW else 1
RELAY_OFF = 1 - RELAY_ON

# Initialize relay in OFF state
relay = Pin(14, Pin.OUT, value=RELAY_OFF)  # D5

# Initialize 16x2 I2C LCD on D1 (SCL, GPIO5) and D2 (SDA, GPIO4)
lcd = None
try:
    from lcd_i2c import init_lcd
    lcd = init_lcd(scl_pin=5, sda_pin=4)
except Exception as _lcd_err:
    print("[LCD] Initialization notice:", _lcd_err)

wifi = network.WLAN(network.STA_IF)
wifi.active(True)


def display_status(data, pump_on, mode):
    """Renders current measurements and actuator state to 16x2 LCD."""
    if not lcd:
        return
    try:
        t = data.get("temperature_c")
        h = data.get("humidity_pct")
        s = data.get("soil_moisture_pct")
        t_str = f"T:{t:.1f}C" if t is not None else "T:--"
        h_str = f"H:{int(h)}%" if h is not None else "H:--"
        s_str = f"S:{int(s)}%" if s is not None else "S:--"
        p_str = "P:ON " if pump_on else "P:OFF"
        m_str = "A" if mode == "auto" else "M"
        lcd.print_line(0, f"{t_str} {h_str}")
        lcd.print_line(1, f"{s_str} {p_str} [{m_str}]")
    except Exception as err:
        print("[LCD] Render notice:", err)


def connect_wifi():
    if wifi.isconnected():
        return True

    print("Connecting to Wi-Fi...")
    if lcd:
        lcd.print_line(0, "Connecting WiFi")
        lcd.print_line(1, str(WIFI_SSID)[:16])


    try:
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    except OSError as error:
        print("Wi-Fi error:", error)
        return False

    started = time.ticks_ms()

    while not wifi.isconnected():
        if time.ticks_diff(time.ticks_ms(), started) > 10000:
            print("Wi-Fi connection timed out")
            return False
        time.sleep_ms(200)

    print("Wi-Fi connected:", wifi.ifconfig()[0])
    if lcd:
        lcd.print_line(0, "WiFi Connected")
        lcd.print_line(1, str(wifi.ifconfig()[0])[:16])
    return True



def read_soil():
    total = 0

    # Average five measurements
    for _ in range(5):
        total += soil_sensor.read()
        time.sleep_ms(20)

    raw = total // 5

    difference = SOIL_DRY_RAW - SOIL_WET_RAW
    if difference == 0:
        raise ValueError("Invalid soil calibration")

    moisture = (SOIL_DRY_RAW - raw) * 100 / difference
    moisture = max(0, min(100, moisture))

    return raw, round(moisture, 1)


def read_sensors():
    temperature = None
    humidity = None

    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
    except OSError as error:
        print("DHT11 error:", error)

    try:
        raw, moisture = read_soil()
    except Exception as error:
        print("Soil sensor error:", error)
        raw, moisture = None, None

    return {
        "device_id": DEVICE_ID,
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "soil_raw": raw,
        "soil_moisture_pct": moisture,
        "motion": bool(pir_sensor.value()),
    }


def api_request(method, path, payload=None):
    if not wifi.isconnected():
        return None

    headers = {"Content-Type": "application/json", "X-Device-Token": DEVICE_TOKEN,
               "X-Device-Key": DEVICE_TOKEN}

    response = None

    try:
        url = API_BASE_URL + path

        if method == "POST":
            response = requests.post(
                url, data=ujson.dumps(payload), headers=headers, timeout=3
            )
        else:
            response = requests.get(url, headers=headers, timeout=3)

        if response.status_code != 200:
            print("API HTTP status:", response.status_code)
            return None

        return response.json()

    except Exception as error:
        print("API error:", error)
        return None

    finally:
        if response is not None:
            response.close()
        gc.collect()


def main():
    print("Starting plant monitoring...")

    # Safe state on startup
    relay.value(RELAY_OFF)

    pump_on = False
    pump_started = None
    pump_stopped = None

    mode = "auto"
    manual_requested = False

    last_command_id = None
    boot_poll = True
    pending_ack = None
    last_report = None
    last_reconnect = None
    last_press = None
    previous_button = button.value()

    data = {"soil_moisture_pct": None}

    connect_wifi()

    while True:
        now = time.ticks_ms()

        # Physical button: toggle manual pump request
        current_button = button.value()

        if current_button == 0 and previous_button == 1:
            if last_press is None or time.ticks_diff(now, last_press) > 250:
                if mode == "manual":
                    manual_requested = not manual_requested
                else:
                    manual_requested = not pump_on

                mode = "manual"
                last_press = now
                print("Button:", manual_requested)

        previous_button = current_button

        # Read sensors and exchange data every 5 seconds
        if (
            last_report is None
            or time.ticks_diff(now, last_report) >= REPORT_INTERVAL_MS
        ):
            last_report = now
            data = read_sensors()

            # Retry an ACK without applying the same command twice.
            if pending_ack and wifi.isconnected() and not pump_on:
                pending_ack[1]["confirmed_state"] = pump_on
                if api_request("POST", "/api/v1/devices/" + DEVICE_ID + "/commands/" + pending_ack[0] + "/ack", pending_ack[1]):
                    pending_ack = None

            # Do not spend a network timeout polling while the pump is active.
            command = None
            command_status = None
            if wifi.isconnected() and not pump_on and not pending_ack:
                command = api_request(
                    "GET", "/api/v1/devices/" + DEVICE_ID + "/commands"
                )
                if command is not None:
                    command = command.get("command") if command.get("has_command") else None
                    if command and command.get("command_id") != last_command_id:
                        mode, manual_requested, command_status = apply_command(
                            command, mode, manual_requested, not boot_poll
                        )
                        last_command_id = command.get("command_id")
                    boot_poll = False

            # Safety and control decisions
            now = time.ticks_ms()
            moisture = data["soil_moisture_pct"]

            if moisture is None or mode == "off":
                wanted = False

            elif mode == "manual":
                wanted = manual_requested

            else:
                # Hysteresis prevents rapid ON/OFF switching
                threshold = PUMP_STOP_ABOVE if pump_on else PUMP_START_BELOW
                wanted = moisture < threshold

            if pump_on:
                elapsed = time.ticks_diff(now, pump_started)

                if not wanted or elapsed >= MAX_PUMP_ON_MS:
                    relay.value(RELAY_OFF)
                    pump_on = False
                    pump_stopped = now

                    if mode == "manual":
                        manual_requested = False

                    print("Pump OFF")

            elif wanted:
                cooled = (
                    pump_stopped is None
                    or time.ticks_diff(now, pump_stopped) >= PUMP_COOLDOWN_MS
                )

                if cooled:
                    relay.value(RELAY_ON)
                    pump_on = True
                    pump_started = now
                    print("Pump ON")

            # Publish actual state, not just requested state
            data["pump_on"] = pump_on
            data["mode"] = mode
            display_status(data, pump_on, mode)

            print("Telemetry:", data)

            if wifi.isconnected():
                if command and command_status:
                    expected = str(command.get("value")).lower() == "true"
                    if command.get("action") == "SET_PUMP" and pump_on != expected:
                        command_status = "REJECTED"
                    pending_ack = (command["command_id"], {
                        "status": command_status,
                        "confirmed_state": pump_on,
                        "reason": "Relay GPIO state after firmware safety checks; no flow sensor fitted",
                    })
                    if api_request("POST", "/api/v1/devices/" + DEVICE_ID + "/commands/" + pending_ack[0] + "/ack", pending_ack[1]):
                        pending_ack = None
                if not pump_on:
                    result = api_request("POST", "/api/device/telemetry", data)
                    print("Published:", result is not None)

        # Enforce pump safety between reporting intervals
        if pump_on:
            elapsed = time.ticks_diff(time.ticks_ms(), pump_started)

            if elapsed >= MAX_PUMP_ON_MS or (mode == "manual" and not manual_requested):
                relay.value(RELAY_OFF)
                pump_on = False
                pump_stopped = time.ticks_ms()

                if mode == "manual":
                    manual_requested = False

                display_status(data, pump_on, mode)
                print("Pump safety stop")

        # Retry networking without blocking an active pump
        now = time.ticks_ms()

        if not wifi.isconnected() and not pump_on:
            if last_reconnect is None or time.ticks_diff(now, last_reconnect) >= 15000:
                last_reconnect = now
                connect_wifi()

        time.sleep_ms(100)


if __name__ in ("__main__", "__mp_main__"):
    try:
        main()
    except KeyboardInterrupt:
        relay.value(RELAY_OFF)
        if lcd:
            lcd.print_line(0, "Plant Station")
            lcd.print_line(1, "Relay SAFE / OFF")
        print("Stopped")
    except Exception as error:
        relay.value(RELAY_OFF)
        if lcd:
            lcd.print_line(0, "System Error")
            lcd.print_line(1, "Relay SAFE / OFF")
        print("Fatal error:", error)
        raise
