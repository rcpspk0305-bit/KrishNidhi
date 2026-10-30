# Local hardware and prediction setup

## Start the website and API

From the repository root (two terminals):

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev -- --hostname 0.0.0.0
```

Open `http://localhost:3000/dashboard`. On another device on the same private
network use `http://<computer-LAN-IP>:3000/dashboard`. The Next.js server proxies
`/backend/*` to FastAPI, including SSE. No browser-side localhost address is needed.
For Docker set server-only `BACKEND_URL=http://backend:8000`. The optional
`NEXT_PUBLIC_API_URL` override must include `/api/v1`; restart Next.js after changing it.
Allow ports 3000 and 8000 on Windows Firewall for the private network only.
The current review preview instead uses backend port 8001 and dashboard port 3002;
its `frontend/.env.local` points to 8001. Change `BACKEND_URL` to
`http://127.0.0.1:8000` when using the commands above.
Use a trusted LAN: the existing dashboard control endpoints do not have operator authentication.

## USB sensors without Wi-Fi

The board must already have `main.py`, `config.py`, and `lcd_i2c.py` installed.
Close Arduino/serial monitors before taking ownership of the COM port.

```powershell
python -m pip install mpremote
python hardware/usb_telemetry_bridge.py --port COM5 --once
python hardware/usb_telemetry_bridge.py --port COM5
```

This interrupts the board's current application and holds the relay OFF. It forwards
actual sensor readings through the computer's USB connection, not simulated readings.
It does not execute dashboard pump commands. Select `plant-01` on the dashboard.
Set `NEXT_PUBLIC_SENSOR_ONLY=true` in `frontend/.env.local` and restart Next.js
to display the USB connection notice and disable pump controls. Set it to `false`
when switching to Wi-Fi firmware. This UI setting is not an authorization mechanism.
The bridge reads `DEVICE_TOKEN` from the root `.env` or the environment; it must match
the backend. Stop with Ctrl+C; restart/reset the board to resume Wi-Fi firmware.

## Wi-Fi telemetry and pump commands

Privately edit `hardware/config.py`: set `WIFI_SSID`, `WIFI_PASSWORD`,
`API_BASE_URL=http://<computer-LAN-IP>:8000`, `DEVICE_ID=plant-01`, and a matching
`DEVICE_TOKEN`. Never commit real credentials. Both devices need the same 2.4 GHz
LAN without client isolation. The computer's address at implementation time was
`192.168.0.194`; verify with `ipconfig` because DHCP can change it.

Install the three current firmware modules after configuring credentials:

```powershell
python -m mpremote connect COM5 fs cp hardware/config.py :config.py
python -m mpremote connect COM5 fs cp hardware/command_protocol.py :command_protocol.py
python -m mpremote connect COM5 fs cp hardware/main.py :main.py
python -m mpremote connect COM5 reset
```

MicroPython now polls `/api/v1/devices/{id}/commands` and acknowledges commands on
the same API the dashboard uses. OFF mode, sensor faults, cooldown and runtime
limits remain firmware responsibilities. A pump ON command present on the first
successful poll is rejected. Confirmed state describes relay GPIO, not measured
water flow. Polling is suspended while the pump runs; remote stop can therefore
wait for the local runtime limit. Verify watchdog timing on physical hardware;
HTTP timeout settings are not a hard real-time guarantee. Do not run the USB bridge
and Wi-Fi application together.

Do not overwrite `hardware/config.py` on the board until its private credentials
have been configured. The Arduino firmware under `firmware/` uses the separate
device `esp8266-plant-01`; select that device if using the Arduino build instead.

## Prediction methods

`POST /predict` preserves `recommended_crop` and adds the method, top three
suitability rankings, limitations, and validation metrics when a trained model
is loaded. The default is deterministic range-based scoring, not trained ML.
Scores are not probabilities. TDS cannot replace N/P/K measurements.

To train from your own real labelled CSV, use columns
`N,P,K,temperature,humidity,ph,rainfall,label` with consistent units and rainfall
periods. At least two crops and five samples per crop are required; substantially
more representative field data is needed for useful validation.

```powershell
cd backend
python -m ml.train path/to/crops.csv --output ml/crop-model.json
$env:CROP_MODEL_PATH = (Resolve-Path ml/crop-model.json).Path
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Training uses a reproducible stratified 80/20 split and fits standardization only
on training data. It exports a JSON nearest-centroid model and reports held-out
accuracy and balanced accuracy. The holdout is not independent farm/season
validation. No dataset or model accuracy is claimed by this change.

Plant recommendations include a Theil-Sen soil moisture forecast fitted to actual
recorded history. At least four valid samples spanning an hour are required. Pump
activity, sustained moisture refills and long gaps reset the fitting window.
Stale/noisy readings withhold estimates. Threshold deadlines are limited to the
observed duration and at most six hours. Forecasts advise users; they never actuate
the pump. Frequent telemetry may take an hour to build enough history.
