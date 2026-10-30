"""Forward real ESP8266 sensor readings over USB to the local FastAPI backend.

Telemetry-only bridge: keeps the relay OFF. Use Wi-Fi firmware for pump control.
Requires: pip install mpremote
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request, urlopen

MARKER = 'USB_TELEMETRY:'
PROBE = (
    "import main,ujson; main.relay.value(main.RELAY_OFF); "
    "d=main.read_sensors(); d['pump_on']=False; d['mode']='manual'; "
    "print('USB_TELEMETRY:'+ujson.dumps(d))"
)


def parse_reading(output):
    for line in output.splitlines():
        if line.startswith(MARKER):
            data = json.loads(line[len(MARKER):])
            if not any(data.get(key) is not None for key in ('temperature_c', 'humidity_pct', 'soil_moisture_pct')):
                raise ValueError('No valid sensor readings received')
            return data
    raise ValueError('Board did not return sensor telemetry; ensure hardware/main.py is installed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--api', default='http://127.0.0.1:8000')
    parser.add_argument('--interval', type=float, default=5)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    except ImportError:
        pass
    token = os.getenv('DEVICE_TOKEN', 'replace-with-a-long-random-secret')
    print('USB telemetry only. Relay held OFF; Wi-Fi firmware must not run concurrently.', flush=True)
    while True:
        try:
            result = subprocess.run([sys.executable, '-m', 'mpremote', 'connect', args.port,
                                     'exec', PROBE], capture_output=True, text=True, timeout=20, check=True)
            data = parse_reading(result.stdout)
            request = Request(args.api.rstrip('/') + '/api/device/telemetry',
                              data=json.dumps(data).encode(),
                              headers={'Content-Type': 'application/json', 'X-Device-Token': token})
            with urlopen(request, timeout=5) as response:
                if response.status != 200:
                    raise RuntimeError('Backend rejected telemetry')
            print(json.dumps(dict(device_id=data['device_id'], temperature=data.get('temperature_c'),
                                  humidity=data.get('humidity_pct'), soil_moisture=data.get('soil_moisture_pct'),
                                  pump_on=False, source='usb_hardware')), flush=True)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            print(f'USB bridge error: {type(error).__name__}: {error}', file=sys.stderr, flush=True)
            if args.once:
                raise SystemExit(1)
        if args.once:
            break
        time.sleep(max(2, args.interval))


if __name__ == '__main__':
    main()
