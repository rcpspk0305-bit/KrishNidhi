WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# IP address of the computer hosting FastAPI (LAN reachable IP)
API_BASE_URL = "http://192.168.0.194:8000"


DEVICE_ID = "plant-01"
DEVICE_TOKEN = "replace-with-a-long-random-secret"

# Replace these after calibrating your sensor
SOIL_DRY_RAW = 850
SOIL_WET_RAW = 350

# Many relay modules are active LOW
RELAY_ACTIVE_LOW = True

# Automatic irrigation thresholds
PUMP_START_BELOW = 35
PUMP_STOP_ABOVE = 55

# Pump safety limits
MAX_PUMP_ON_MS = 10000
PUMP_COOLDOWN_MS = 60000

# Sensor reporting interval
REPORT_INTERVAL_MS = 5000
