import streamlit as st
import sys
import os
import random
import asyncio
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Bridge Streamlit Cloud secrets to environment variables if present
try:
    if hasattr(st, "secrets"):
        for sec_key, sec_val in st.secrets.items():
            if isinstance(sec_val, str) and sec_key not in os.environ:
                os.environ[sec_key] = sec_val
except Exception:
    pass

# Ensure the backend directory is in the path for importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import from backend application
try:
    from app.core.database import engine, SessionLocal, init_db
    from app.models import db_models
    from app.services.ml_service import predict_crop
    from app.services.llm_service import generate_action_plan, generate_chat_response, client_model
    from app.services.vision_service import detect_disease_from_image
    from app.models.schemas import SensorData, GenAIRequest, ChatRequest
    from app.core.config import settings
    from app.services.mqtt_service import latest_iot_data, iot_metadata, start_mqtt_background
    try:
        from app.services.assistant_service import answer_question as assistant_answer_question, AssistantUnavailable
        from app.schemas.assistant_schemas import AssistantRequest, AssistantMessage
    except ImportError:
        assistant_answer_question = None
        AssistantUnavailable = Exception
        AssistantRequest = None
        AssistantMessage = None
except ImportError as e:
    st.error(f"Failed to import backend modules. Make sure you run streamlit from the project root. Error: {e}")
    st.stop()

# Initialize DB tables and schema migrations
init_db()

# Ensure MQTT background subscriber is active
start_mqtt_background()

# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Helper function to run async functions safely in Streamlit
def run_async(coro):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Populate initial historical data if DB is empty
def populate_initial_data(db):
    dev = db.query(db_models.Device).filter(db_models.Device.id == "esp32-node-01").first()
    if not dev:
        dev = db_models.Device(
            id="esp32-node-01",
            name="Smart Plant Station #1",
            api_key_hash="seed_hash",
            status="online",
            control_mode="AUTO",
            pump_state=False,
            last_seen=datetime.now(timezone.utc)
        )
        db.add(dev)
        db.commit()

    prof = db.query(db_models.PlantProfile).filter(db_models.PlantProfile.device_id == "esp32-node-01").first()
    if not prof:
        prof = db_models.PlantProfile(
            device_id="esp32-node-01",
            plant_name="Monstera Deliciosa",
            plant_type="Tropical Foliage",
            preferred_temp_min=18.0,
            preferred_temp_max=30.0,
            preferred_humidity_min=50.0,
            preferred_humidity_max=75.0,
            preferred_moisture_min=30.0,
            preferred_moisture_max=55.0
        )
        db.add(prof)
        db.commit()

    count = db.query(db_models.SensorReading).count()
    if count == 0:
        now = datetime.now(timezone.utc)
        for i in range(24, 0, -1):
            timestamp = now - pd.Timedelta(hours=i)
            reading = db_models.SensorReading(
                device_id="esp32-node-01",
                timestamp=timestamp,
                temperature=round(24.5 + random.uniform(-1.5, 1.5), 1),
                humidity=round(58.0 + random.uniform(-4, 4), 1),
                soil_moisture=round(48.0 + random.uniform(-5, 5), 1),
                soil_raw=int(round(490 + random.uniform(-20, 20))),
                motion_detected=False,
                pump_on=False,
                control_mode="AUTO",
                ph=round(6.5 + random.uniform(-0.1, 0.1), 2),
                rainfall=round(40.0 + random.uniform(-5, 5), 1),
                n=round(80.0 + random.uniform(-4, 4), 1),
                p=round(48.0 + random.uniform(-2, 2), 1),
                k=round(40.0 + random.uniform(-2, 2), 1),
                tds=round(140.0 + random.uniform(-10, 10), 1)
            )
            db.add(reading)
        db.commit()

db = get_db()
populate_initial_data(db)

# Streamlit Page Config
st.set_page_config(
    page_title="KrishiNidhi Botanical Console - Smart Plant & Irrigation Station",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Botanical Editorial Styling matching the Next.js Botanical Console
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-canvas: #fbf9f5;
        --bg-subtle: #f3efe6;
        --surface-card: #ffffff;
        --text-primary: #192a21;
        --text-secondary: #4a5c52;
        --text-muted: #73847a;
        --forest-800: #1b3527;
        --forest-700: #254836;
        --forest-600: #315c45;
        --forest-100: #eaf1ec;
        --terracotta-700: #9e3f26;
        --terracotta-100: #faece8;
        --dew-700: #255d6e;
        --dew-100: #eaf4f7;
        --gold-700: #8c6014;
        --gold-100: #fcf4e4;
        --border-subtle: rgba(25, 42, 33, 0.08);
        --border-default: rgba(25, 42, 33, 0.14);
    }

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f6f3eb !important;
        border-right: 1px solid var(--border-default) !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Botanical Top Banner */
    .botanical-topbar {
        background: #ffffff;
        border: 1px solid var(--border-default);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 12px rgba(25, 42, 33, 0.03);
    }
    .botanical-tag {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--forest-700);
        margin-bottom: 2px;
    }
    .botanical-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.15;
    }

    /* Cards */
    .botanical-card {
        background: #ffffff;
        border: 1px solid var(--border-default);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(25, 42, 33, 0.03);
    }

    /* Status Pills */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pill-forest {
        background-color: var(--forest-100);
        color: var(--forest-700);
        border: 1px solid rgba(37, 72, 54, 0.2);
    }
    .pill-terracotta {
        background-color: var(--terracotta-100);
        color: var(--terracotta-700);
        border: 1px solid rgba(158, 63, 38, 0.2);
    }
    .pill-dew {
        background-color: var(--dew-100);
        color: var(--dew-700);
        border: 1px solid rgba(37, 93, 110, 0.2);
    }
    .pill-gold {
        background-color: var(--gold-100);
        color: var(--gold-700);
        border: 1px solid rgba(140, 96, 20, 0.2);
    }

    /* Buttons */
    .stButton>button {
        background: #254836 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(37, 72, 54, 0.15) !important;
    }
    .stButton>button:hover {
        background: #1b3527 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 72, 54, 0.25) !important;
    }

    /* Notification items */
    .notification-item {
        background: #f7f4ed;
        border-left: 3px solid var(--forest-600);
        padding: 9px 13px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.86rem;
        color: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# Navigation / Sidebar
st.sidebar.markdown("<p style='font-size:0.75rem; letter-spacing:0.1em; font-weight:700; color:#73847a; text-transform:uppercase; margin-bottom:4px;'>Navigation</p>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='color:#192a21; margin-top:0; margin-bottom:18px; font-family:serif; font-weight:700;'>Botanical Console</h2>", unsafe_allow_html=True)

app_mode = st.sidebar.radio(
    "Select Workspace",
    ["🌿 Smart Plant Station", "🌾 Crop Recommendation", "🍃 Leaf Disease Diagnosis", "🤖 KrishiNidhi AI Chatbot"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size:0.75rem; letter-spacing:0.1em; font-weight:700; color:#73847a; text-transform:uppercase;'>Hardware & AI Status</p>", unsafe_allow_html=True)
has_gemini = "Configured" if settings.GEMINI_API_KEY else "Fallback Mode"
has_assistant = "Configured" if getattr(settings, "OPENROUTER_API_KEY", None) else "Fallback Mode"
st.sidebar.markdown(f"**ESP8266 Link:** `{'Online' if iot_metadata.get('connected') else 'Standby'}`")
st.sidebar.markdown(f"**AI Assistant:** {has_assistant}")
st.sidebar.markdown(f"**Crop Doctor:** {has_gemini}")

# Active alerts container helper
def add_notification(text):
    if "notifications" not in st.session_state:
        st.session_state.notifications = [
            "[07:15:00] Soil moisture at optimal balance for Monstera.",
            "[07:00:00] Hardware linked. Auto irrigation active.",
            "[06:30:00] Ambient temperature stable within microclimate target."
        ]
    st.session_state.notifications.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
    if len(st.session_state.notifications) > 6:
        st.session_state.notifications.pop()

if "notifications" not in st.session_state:
    st.session_state.notifications = [
        "[07:15:00] Soil moisture at optimal balance for Monstera.",
        "[07:00:00] Hardware linked. Auto irrigation active.",
        "[06:30:00] Ambient temperature stable within microclimate target."
    ]


# ----------------- 1. SMART PLANT & IRRIGATION STATION -----------------

if app_mode == "🌿 Smart Plant Station":
    # Top Console Header Bar matching Screenshot 2
    is_live = iot_metadata.get("connected", False)
    status_pill_class = "pill-forest" if is_live else "pill-terracotta"
    status_pill_label = "ESP8266 Live" if is_live else "ESP8266 Offline"

    st.markdown(f"""
    <div class="botanical-topbar">
        <div>
            <div class="botanical-tag">KRISHINIDHI BOTANICAL CONSOLE</div>
            <h1 class="botanical-title">Smart Plant & Irrigation Station</h1>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
            <span class="pill {status_pill_class}">● {status_pill_label}</span>
            <span class="pill pill-dew">((•)) Live SSE: Connected</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch latest plant profile & reading from database
    db = get_db()
    plant_prof = db.query(db_models.PlantProfile).filter(db_models.PlantProfile.device_id == "esp32-node-01").first()
    plant_name = plant_prof.plant_name if plant_prof else "Monstera Deliciosa"
    last_db_reading = db.query(db_models.SensorReading).order_by(db_models.SensorReading.timestamp.desc()).first()

    temp_val = latest_iot_data.get("temperature", 25.5)
    hum_val = latest_iot_data.get("humidity", 40.0)
    soil_val = latest_iot_data.get("soil_moisture", 48.0)
    soil_raw_val = latest_iot_data.get("soil_raw", 490)
    motion_val = latest_iot_data.get("motion_detected", False)
    pump_val = latest_iot_data.get("pump_on", False)
    mode_val = latest_iot_data.get("control_mode", "AUTO")

    # Agronomic health scoring
    if soil_val is not None and 30 <= soil_val <= 60:
        health_status = "Optimal Microclimate"
        health_pill = "pill-forest"
        health_score = 94
    elif soil_val is not None and soil_val < 30:
        health_status = "Soil Moisture Low"
        health_pill = "pill-terracotta"
        health_score = 58
    else:
        health_status = "Attention Recommended"
        health_pill = "pill-gold"
        health_score = 75

    # 1. PLANT HEALTH HERO CARD (Matches Screenshot 2 Hero)
    st.markdown(f"""
    <div class="botanical-card" style="padding: 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 18px;">
                <div style="width: 56px; height: 56px; border-radius: 16px; background: #eaf1ec; border: 1px solid #d3e2d7; display: flex; align-items: center; justify-content: center; font-size: 28px;">
                    🌱
                </div>
                <div>
                    <h2 style="font-family: 'Newsreader', Georgia, serif; font-size: 2.2rem; font-weight: 700; color: #192a21; margin: 0;">{plant_name}</h2>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;">
                        <span class="pill {health_pill}">Health: {health_status}</span>
                        <span class="pill {status_pill_class}">{status_pill_label}</span>
                        <span class="pill pill-dew">Mode: {mode_val}</span>
                    </div>
                    <p style="margin: 8px 0 0 0; color: #73847a; font-size: 0.85rem;">
                        ⏱️ Telemetry Timestamp: <b style="color: #4a5c52;">{datetime.now().strftime('%I:%M:%S %p')}</b> | Awaiting continuous sensor tick
                    </p>
                </div>
            </div>
            <div style="background: #f5f2ea; border: 1px solid #e8e3da; border-radius: 14px; padding: 14px 22px; text-align: center; min-width: 150px;">
                <span style="display:block; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; color: #73847a;">AGRONOMIC INDEX</span>
                <span style="font-family: 'Newsreader', Georgia, serif; font-size: 2.4rem; font-weight: 700; color: #1b3527;">{health_score}</span>
                <span style="font-size: 0.85rem; color: #73847a; font-weight: normal;"> / 100</span>
            </div>
        </div>
        
        <!-- Snapshot quick telemetry ribbon -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 20px; padding-top: 18px; border-top: 1px solid rgba(25, 42, 33, 0.08);">
            <div style="background: #f5f2ea; border: 1px solid #e8e3da; border-radius: 12px; padding: 12px 16px;">
                <div style="font-size: 0.8rem; color: #4a5c52; font-weight: 600;">🌡️ Temperature</div>
                <div style="font-family: 'Newsreader', Georgia, serif; font-size: 1.7rem; font-weight: 700; color: #192a21; margin-top: 2px;">{temp_val}°C</div>
            </div>
            <div style="background: #f5f2ea; border: 1px solid #e8e3da; border-radius: 12px; padding: 12px 16px;">
                <div style="font-size: 0.8rem; color: #4a5c52; font-weight: 600;">💨 Humidity</div>
                <div style="font-family: 'Newsreader', Georgia, serif; font-size: 1.7rem; font-weight: 700; color: #192a21; margin-top: 2px;">{hum_val}%</div>
            </div>
            <div style="background: #f5f2ea; border: 1px solid #e8e3da; border-radius: 12px; padding: 12px 16px;">
                <div style="font-size: 0.8rem; color: #4a5c52; font-weight: 600;">💧 Soil Moisture</div>
                <div style="font-family: 'Newsreader', Georgia, serif; font-size: 1.7rem; font-weight: 700; color: #192a21; margin-top: 2px;">{soil_val}%</div>
            </div>
            <div style="background: #f5f2ea; border: 1px solid #e8e3da; border-radius: 12px; padding: 12px 16px;">
                <div style="font-size: 0.8rem; color: #4a5c52; font-weight: 600;">🌱 Control Mode</div>
                <div style="font-family: 'Newsreader', Georgia, serif; font-size: 1.5rem; font-weight: 700; color: #254836; margin-top: 4px;">{mode_val}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. DETAILED SENSOR CARDS GRID (Matches Screenshot 2's 4 physical cards)
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)

    with col_c1:
        st.markdown(f"""
        <div class="botanical-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#4a5c52;">
                    <span>🌡️ Ambient Temp (DHT11)</span>
                </div>
                <span style="font-family:monospace; font-size:0.72rem; color:#73847a;">GPIO 12 / D6</span>
            </div>
            <div style="font-family:'Newsreader', Georgia, serif; font-size:2.4rem; font-weight:700; color:#192a21; margin:8px 0;">
                {temp_val} <span style="font-size:1rem; font-weight:600; color:#73847a;">°C</span>
            </div>
            <div style="padding-top:10px; border-top:1px solid #e8e3da; font-size:0.75rem; color:#73847a;">
                <div>Target: 18.0°C – 30.0°C</div>
                <p style="margin:4px 0 0 0; font-weight:600; color:#254836;">Optimal Microclimate</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown(f"""
        <div class="botanical-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#4a5c52;">
                    <span>💨 Relative Humidity</span>
                </div>
                <span style="font-family:monospace; font-size:0.72rem; color:#73847a;">1-Wire Digital</span>
            </div>
            <div style="font-family:'Newsreader', Georgia, serif; font-size:2.4rem; font-weight:700; color:#192a21; margin:8px 0;">
                {hum_val} <span style="font-size:1rem; font-weight:600; color:#73847a;">% RH</span>
            </div>
            <div style="padding-top:10px; border-top:1px solid #e8e3da; font-size:0.75rem; color:#73847a;">
                <div>Target: 50% – 75% RH</div>
                <p style="margin:4px 0 0 0; font-weight:600; color:#255d6e;">Comfort Zone</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        soil_bar_width = min(100, max(0, int(soil_val)))
        soil_color = "#315c45" if soil_val >= 30 else "#bd5134"
        st.markdown(f"""
        <div class="botanical-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#4a5c52;">
                    <span>💧 Soil Moisture (LM393)</span>
                </div>
                <span style="font-family:monospace; font-size:0.72rem; color:#73847a;">ADC 0 / A0</span>
            </div>
            <div style="display:flex; align-items:baseline; gap:6px; margin:8px 0;">
                <span style="font-family:'Newsreader', Georgia, serif; font-size:2.4rem; font-weight:700; color:#192a21;">{soil_val}</span>
                <span style="font-size:1rem; font-weight:600; color:#73847a;">%</span>
                <span style="margin-left:auto; font-family:monospace; font-size:0.72rem; color:#73847a;">Raw: {soil_raw_val}</span>
            </div>
            <div style="width:100%; height:8px; background:#f0ece2; border-radius:999px; overflow:hidden; margin:8px 0;">
                <div style="width:{soil_bar_width}%; height:100%; background:{soil_color}; border-radius:999px;"></div>
            </div>
            <div style="padding-top:10px; border-top:1px solid #e8e3da; font-size:0.75rem; color:#73847a; display:flex; justify-content:space-between;">
                <span>Auto-on: &lt;30%</span>
                <span>Target cutoff: 55%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c4:
        motion_label = "Movement Detected 🐾" if motion_val else "Field Clear 🌿"
        motion_badge_bg = "#faece8" if motion_val else "#eaf1ec"
        motion_badge_color = "#9e3f26" if motion_val else "#254836"
        st.markdown(f"""
        <div class="botanical-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#4a5c52;">
                    <span>🐾 PIR Motion Sensor</span>
                </div>
                <span style="font-family:monospace; font-size:0.72rem; color:#73847a;">GPIO 13 / D7</span>
            </div>
            <div style="font-family:'Newsreader', Georgia, serif; font-size:1.7rem; font-weight:700; color:{motion_badge_color}; margin:14px 0 10px 0;">
                {motion_label}
            </div>
            <div style="padding-top:10px; border-top:1px solid #e8e3da; font-size:0.75rem; color:#73847a;">
                <span>Passive infrared detection around planter perimeter</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. IRRIGATION PUMP CONTROLLER
    st.markdown("### 🚰 Smart Irrigation Pump Controller")
    col_pump_info, col_pump_actions = st.columns([2, 1])

    with col_pump_info:
        pump_state_str = "ACTIVE (PUMPING WATER)" if pump_val else "STANDBY / IDLE"
        pump_state_color = "#254836" if pump_val else "#73847a"
        st.markdown(f"""
        <div class="botanical-card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
                <span class="botanical-tag">Submersible 5V Relay IN (Active LOW on D5)</span>
                <div style="font-family:'Newsreader', Georgia, serif; font-size:1.9rem; font-weight:700; color:{pump_state_color}; margin-top:2px;">
                    {pump_state_str}
                </div>
                <p style="margin:4px 0 0 0; font-size:0.82rem; color:#73847a;">
                    Safety Failsafes: <b>15s continuous runtime watchdog</b> | <b>60s rest cooldown limit</b>
                </p>
            </div>
            <div>
                <span class="pill pill-forest" style="font-size:0.9rem;">Mode: {mode_val}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_pump_actions:
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🟢 Start Pump", use_container_width=True):
                latest_iot_data["pump_on"] = True
                latest_iot_data["control_mode"] = "MANUAL"
                db = get_db()
                dev_obj = db.query(db_models.Device).filter(db_models.Device.id == "esp32-node-01").first()
                if dev_obj:
                    dev_obj.pump_state = True
                    dev_obj.control_mode = "MANUAL"
                db.add(db_models.PumpEvent(
                    device_id="esp32-node-01",
                    requested_state=True,
                    confirmed_state=True,
                    source="streamlit_manual",
                    control_mode="MANUAL",
                    reason="Streamlit botanical manual operator override"
                ))
                db.commit()
                add_notification("Irrigation Pump manually started.")
                st.success("Pump Activated!")
                st.rerun()

        with col_act2:
            if st.button("🔴 Stop Pump", use_container_width=True):
                latest_iot_data["pump_on"] = False
                db = get_db()
                dev_obj = db.query(db_models.Device).filter(db_models.Device.id == "esp32-node-01").first()
                if dev_obj:
                    dev_obj.pump_state = False
                db.add(db_models.PumpEvent(
                    device_id="esp32-node-01",
                    requested_state=False,
                    confirmed_state=False,
                    source="streamlit_manual",
                    control_mode=latest_iot_data.get("control_mode", "MANUAL"),
                    reason="Streamlit botanical manual operator stop"
                ))
                db.commit()
                add_notification("Irrigation Pump stopped.")
                st.warning("Pump Stopped.")
                st.rerun()

        if st.button("⚙️ Re-enable AUTO Mode", use_container_width=True):
            latest_iot_data["control_mode"] = "AUTO"
            db = get_db()
            dev_obj = db.query(db_models.Device).filter(db_models.Device.id == "esp32-node-01").first()
            if dev_obj:
                dev_obj.control_mode = "AUTO"
            db.commit()
            add_notification("Switched to autonomous moisture threshold mode.")
            st.rerun()

    st.markdown("---")

    # 4. INTERACTIVE TELEMETRY & ANALYTICS (Preserves Subheader for AppTest)
    st.subheader("Interactive Telemetry & Analytics")

    telemetry_mode = st.radio(
        "Telemetry Source",
        ["🛰️ Real-World Live IoT Stream", "🧪 Manual Telemetry Simulator"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if telemetry_mode == "🛰️ Real-World Live IoT Stream":
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e7e1d8; border-left: 4px solid #254836; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                <div>
                    <b style="color: #254836; font-size: 0.9rem;">{'HARDWARE LIVE & TRANSMITTING' if is_live else 'WAITING FOR HARDWARE TELEMETRY'}</b>
                    <span style="color: #73847a; font-size: 0.85rem; margin-left: 10px;">| Device: <code>esp32-node-01</code></span>
                </div>
                <div style="color: #73847a; font-size: 0.85rem;">
                    Packets: <b>{iot_metadata.get('packet_count', 0)}</b> | Last Seen: <b>{iot_metadata.get('last_packet_time', 'Never')[-8:] if iot_metadata.get('last_packet_time') else 'Never'}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔌 Microcontroller Ingestion Endpoints (ESP8266 & ESP32)"):
            st.markdown("""
            **1. HTTP Telemetry Ingestion (POST):**
            ```bash
            curl -X POST http://localhost:8000/api/devices/esp32-node-01/telemetry \\
              -H "Content-Type: application/json" \\
              -d '{"device_id": "esp32-node-01", "temperature": 25.5, "humidity": 58.0, "soil_moisture": 48.0, "soil_raw": 490, "motion_detected": false, "pump_on": false}'
            ```
            **2. MQTT Ingestion Broker:**
            - **Broker**: `broker.hivemq.com:1883`
            - **Topic**: `agritech/ps10/sensors`
            """)
    else:
        # Simulator Controls
        col_ctr, col_state = st.columns([2, 1])
        with col_ctr:
            st.write("Adjust sensor sliders to test live ML recommendations, soil trends, and pump behavior.")
            
        with col_state:
            if st.button("🔄 Push Live Reading to DB", use_container_width=True):
                db = get_db()
                new_reading = db_models.SensorReading(
                    device_id="esp32-node-01",
                    temperature=latest_iot_data["temperature"],
                    humidity=latest_iot_data["humidity"],
                    ph=latest_iot_data["ph"],
                    rainfall=latest_iot_data["rainfall"],
                    n=latest_iot_data["N"],
                    p=latest_iot_data["P"],
                    k=latest_iot_data["K"],
                    tds=latest_iot_data["tds"],
                    soil_moisture=latest_iot_data.get("soil_moisture", 48.0),
                    soil_raw=int(latest_iot_data.get("soil_raw", 490)),
                    motion_detected=bool(latest_iot_data.get("motion_detected", False)),
                    pump_on=bool(latest_iot_data.get("pump_on", False)),
                    control_mode=str(latest_iot_data.get("control_mode", "AUTO"))
                )
                db.add(new_reading)
                dev_obj = db.query(db_models.Device).filter(db_models.Device.id == "esp32-node-01").first()
                if dev_obj:
                    dev_obj.pump_state = latest_iot_data.get("pump_on", False)
                    dev_obj.control_mode = latest_iot_data.get("control_mode", "AUTO")
                    dev_obj.last_seen = datetime.now(timezone.utc)
                db.commit()
                add_notification(f"Manual reading pushed: Temp {latest_iot_data['temperature']}°C, Moisture {latest_iot_data.get('soil_moisture', 48.0)}%")
                st.success("Reading successfully pushed to Database!")
                st.rerun()

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            latest_iot_data["temperature"] = round(st.slider("Temperature (°C)", 10.0, 50.0, float(latest_iot_data["temperature"]), 0.1), 1)
            latest_iot_data["N"] = round(st.slider("Nitrogen (N)", 0.0, 140.0, float(latest_iot_data["N"]), 1.0), 1)
        with col_s2:
            latest_iot_data["humidity"] = round(st.slider("Humidity (%)", 20.0, 100.0, float(latest_iot_data["humidity"]), 0.1), 1)
            latest_iot_data["P"] = round(st.slider("Phosphorus (P)", 5.0, 140.0, float(latest_iot_data["P"]), 1.0), 1)
        with col_s3:
            latest_iot_data["ph"] = round(st.slider("Soil pH", 3.0, 10.0, float(latest_iot_data["ph"]), 0.1), 2)
            latest_iot_data["K"] = round(st.slider("Potassium (K)", 5.0, 200.0, float(latest_iot_data["K"]), 1.0), 1)
        with col_s4:
            latest_iot_data["rainfall"] = round(st.slider("Rainfall (mm)", 20.0, 300.0, float(latest_iot_data["rainfall"]), 0.1), 1)
            latest_iot_data["tds"] = round(st.slider("Water TDS (ppm)", 0.0, 500.0, float(latest_iot_data.get("tds", 150.0)), 1.0), 1)

        st.markdown("##### 🌿 Smart Plant Hardware Emulation")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            latest_iot_data["soil_moisture"] = round(st.slider("Soil Moisture (%)", 0.0, 100.0, float(latest_iot_data.get("soil_moisture", 48.0)), 0.5), 1)
            latest_iot_data["soil_raw"] = int(1023 - (latest_iot_data["soil_moisture"] / 100.0 * 600))
        with col_p2:
            latest_iot_data["motion_detected"] = st.checkbox("PIR Motion Detected", value=bool(latest_iot_data.get("motion_detected", False)))
        with col_p3:
            latest_iot_data["pump_on"] = st.checkbox("Irrigation Pump Active", value=bool(latest_iot_data.get("pump_on", False)))
        with col_p4:
            current_mode = latest_iot_data.get("control_mode", "AUTO")
            mode_options = ["AUTO", "MANUAL", "OFF"]
            mode_idx = mode_options.index(current_mode) if current_mode in mode_options else 0
            latest_iot_data["control_mode"] = st.selectbox("Control Mode", mode_options, index=mode_idx)

    st.markdown("---")

    # 5. HISTORICAL SENSOR TRENDS & SOIL NPK RATIO
    col_chart_left, col_chart_right = st.columns([2, 1])

    with col_chart_left:
        st.subheader("Historical Sensor Trends")
        db = get_db()
        readings = db.query(db_models.SensorReading).order_by(db_models.SensorReading.timestamp.desc()).limit(30).all()
        
        if readings:
            data_list = []
            for r in reversed(readings):
                data_list.append({
                    "Timestamp": r.timestamp,
                    "Temperature (°C)": r.temperature,
                    "Humidity (%)": r.humidity,
                    "Soil Moisture (%)": r.soil_moisture if r.soil_moisture is not None else 48.0,
                    "pH": r.ph,
                    "Rainfall (mm)": r.rainfall,
                    "Nitrogen": r.n,
                    "Phosphorus": r.p,
                    "Potassium": r.k
                })
            df = pd.DataFrame(data_list)
            
            fig = px.line(
                df, 
                x="Timestamp", 
                y=["Temperature (°C)", "Humidity (%)", "Soil Moisture (%)", "Rainfall (mm)"],
                title="Microclimate & Moisture Trends (Last 24h)",
                color_discrete_sequence=["#bd5134", "#255d6e", "#254836", "#8c6014"]
            )
            fig.update_layout(
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font_color="#192a21",
                font_family="Inter",
                xaxis=dict(showgrid=True, gridcolor='#f0ece2'),
                yaxis=dict(showgrid=True, gridcolor='#f0ece2'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical readings found in database.")

    with col_chart_right:
        st.subheader("Soil NPK Ratio")
        npk_data = pd.DataFrame({
            "Nutrient": ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
            "Current Level": [latest_iot_data["N"], latest_iot_data["P"], latest_iot_data["K"]]
        })
        
        fig_npk = px.bar(
            npk_data,
            x="Nutrient",
            y="Current Level",
            color="Nutrient",
            color_discrete_map={
                "Nitrogen (N)": "#254836",
                "Phosphorus (P)": "#8c6014",
                "Potassium (K)": "#255d6e"
            }
        )
        fig_npk.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_color="#192a21",
            font_family="Inter",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0ece2')
        )
        st.plotly_chart(fig_npk, use_container_width=True)
        
        # Real-time System Status / Recommendation
        sens_data = SensorData(
            N=latest_iot_data["N"],
            P=latest_iot_data["P"],
            K=latest_iot_data["K"],
            temperature=latest_iot_data["temperature"],
            humidity=latest_iot_data["humidity"],
            ph=latest_iot_data["ph"],
            rainfall=latest_iot_data["rainfall"],
            tds=latest_iot_data.get("tds", 150.0)
        )
        rec_crop = predict_crop(sens_data)
        
        st.markdown(f"""
        <div class="botanical-card" style="border-left: 4px solid #254836;">
            <div class="botanical-tag">Live ML Agronomy Match</div>
            <div style="font-family:'Newsreader', Georgia, serif; color: #192a21; font-size: 2rem; font-weight: 700; margin-top: 4px;">{rec_crop}</div>
            <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: #73847a;">Optimal crop match for current soil telemetry profile.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### Operator Log Stream")
        for log in st.session_state.notifications[:4]:
            st.markdown(f'<div class="notification-item">{log}</div>', unsafe_allow_html=True)


# ----------------- 2. CROP RECOMMENDATION MODULE -----------------

elif app_mode == "🌾 Crop Recommendation":
    st.subheader("Soil-Specific Crop Advisor Sandbox")
    st.write("Tune the soil and microclimate parameters below to compute crop suitability recommendations using the ML model.")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Input Soil Parameters")
        N = st.slider("Nitrogen (N)", 0.0, 140.0, 80.0, 1.0)
        P = st.slider("Phosphorus (P)", 5.0, 140.0, 50.0, 1.0)
        K = st.slider("Potassium (K)", 5.0, 205.0, 40.0, 1.0)
        ph = st.slider("Soil pH Level", 3.5, 9.0, 6.5, 0.1)
        
    with col2:
        st.markdown("### Input Weather & Telemetry")
        temp = st.slider("Environment Temp (°C)", 10.0, 50.0, 26.0, 0.5)
        hum = st.slider("Air Humidity (%)", 20.0, 98.0, 60.0, 1.0)
        rain = st.slider("Expected Rainfall (mm)", 20.0, 300.0, 100.0, 1.0)
        tds = st.slider("Irrigation Water TDS (ppm)", 0.0, 500.0, 140.0, 10.0)

    if st.button("🌾 Run Suitability Engine"):
        sensor_pydantic = SensorData(
            N=N, P=P, K=K,
            temperature=temp,
            humidity=hum,
            ph=ph,
            rainfall=rain,
            tds=tds
        )
        rec = predict_crop(sensor_pydantic)
        
        st.markdown("---")
        st.markdown(f"""
        <div class="botanical-card" style="border-left: 5px solid #254836;">
            <div class="botanical-tag">Recommended Specimen</div>
            <h1 style="font-family:'Newsreader', Georgia, serif; color: #192a21; margin: 8px 0; font-size: 2.8rem; font-weight:700;">{rec}</h1>
            <p style="color: #4a5c52; margin-bottom: 0; font-size: 0.95rem;">
                Based on Nitrogen level of <b>{N}</b>, soil pH <b>{ph}</b>, humidity <b>{hum}%</b> and rainfall of <b>{rain}mm</b>, 
                the model suggests cultivating <b>{rec}</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        crop_details = {
            "Rice": "Requires high moisture (humidity > 75%) and rainfall > 150mm. Flooded cultivation or heavy clay soils are ideal.",
            "Potato": "Slightly acidic soil (pH < 6.0) is highly beneficial. Prefers cooler temperature ranges and well-draining soil.",
            "Cotton": "Grows best in hot regions (temp > 30°C) with dry to medium humidity. Requires adequate sun exposure.",
            "Maize": "Nitrogen-heavy feeder. Ideal for high N content (> 80). Requires moderate rainfall and warm temperatures.",
            "Wheat": "Ideal crop for balanced soils and moderate environments. Grown extensively in winter/spring schedules.",
            "Chickpea": "A leguminous crop which thrives on residual soil moisture. Good for low-nitrogen soils as it fixes nitrogen.",
            "Coffee": "Thrives in subtropical/tropical temperatures with high rain. Grown primarily in shady, highland terrains.",
            "Apple": "High-altitude fruit crop requiring cooler weather and neutral soil pH.",
            "Grapes": "Thrives on dry slopes with good exposure. Tolerates low water budgets well once established."
        }
        
        detail = crop_details.get(rec, "Optimal growth guidelines: Maintain consistent NPK monitoring and automate irrigation schedules using live IoT controllers.")
        st.info(detail)


# ----------------- 3. LEAF DISEASE DIAGNOSIS (VISION) -----------------

elif app_mode == "🍃 Leaf Disease Diagnosis":
    st.subheader("AI Vision Disease Detector")
    st.write("Upload a picture of a crop leaf to identify diseases and generate a tailored agronomic action plan.")

    uploaded_file = st.file_uploader("Upload Leaf Snapshot (JPEG/PNG)", type=["jpg", "jpeg", "png"])
    language = st.selectbox("Preferred Communication Language", ["English", "Telugu", "Hindi", "Spanish", "French"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col_img, col_diag = st.columns([1, 1])
        
        with col_img:
            st.image(image, caption="Uploaded Crop Leaf", use_container_width=True)
            
        with col_diag:
            st.markdown("### Analysis Pipeline")
            
            with st.spinner("Analyzing image features via Gemini..."):
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                disease, confidence, bbox = detect_disease_from_image(image_bytes)
                
            st.success("Diagnosis Complete!")
            st.markdown(f"""
            <div class="botanical-card" style="border-left: 5px solid #254836;">
                <div class="botanical-tag">Identified Condition</div>
                <h2 style="font-family:'Newsreader', Georgia, serif; color: #192a21; margin: 4px 0; font-size:2.2rem; font-weight: 700;">{disease}</h2>
                <p style="margin: 0; color: #73847a;">Confidence: <b>{confidence*100:.1f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Agronomic Action Plan")
            with st.spinner("Generating Action Plan..."):
                req = GenAIRequest(
                    crop="Leaf",
                    disease=disease,
                    sensor_data={
                        "temperature": latest_iot_data["temperature"],
                        "humidity": latest_iot_data["humidity"],
                        "ph": latest_iot_data["ph"],
                        "tds": latest_iot_data.get("tds", 150.0),
                        "N": latest_iot_data["N"],
                        "P": latest_iot_data["P"],
                        "K": latest_iot_data["K"]
                    },
                    language=language
                )
                action_plan = run_async(generate_action_plan(req))
            
            st.markdown(action_plan)


# ----------------- 4. KRISHINIDHI AI CHATBOT / ASSISTANT -----------------

elif app_mode == "🤖 KrishiNidhi AI Chatbot":
    st.subheader("KrishiNidhi Agronomist Assistant")
    st.write("Ask agricultural & smart plant monitoring questions in your preferred language. The assistant leverages generative AI with automatic fallback to our comprehensive agronomic compendium.")
    
    chat_lang = st.selectbox("Preferred Chat Language", ["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Spanish"])
    lang_code = "te" if "Telugu" in chat_lang else ("hi" if "Hindi" in chat_lang else "en")

    # Live plant telemetry context banner
    with st.expander("🌱 View Live Plant Monitoring Context", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Soil Moisture", f"{latest_iot_data.get('soil_moisture', 48.0)}%")
        c2.metric("Temperature", f"{latest_iot_data.get('temperature', 25.5)}°C")
        c3.metric("Humidity", f"{latest_iot_data.get('humidity', 40.0)}%")
        c4.metric("Pump State", "ON" if latest_iot_data.get("pump_on", False) else "OFF")

    # Suggested Prompts
    st.markdown("<p style='font-size:0.85rem; color:#4a5c52; margin-bottom:6px;'>Suggested Inquiries:</p>", unsafe_allow_html=True)
    suggested_cols = st.columns(3)
    suggested_query = None
    if lang_code == "te":
        prompts = [
            "నా మొక్కకు సరైన నేల తేమ ఎంత ఉండాలి?",
            "టమాటా ఆకు మచ్చల నివారణ ఎలా చేయాలి?",
            "పంపు ఆటోమేటిక్ ఇరిగేషన్ ఎలా పనిచేస్తుంది?"
        ]
    elif lang_code == "hi":
        prompts = [
            "पौधे के लिए उचित मिट्टी की नमी क्या है?",
            "टमाटर की पत्तियों के रोगों का इलाज कैसे करें?",
            "स्वचालित सिंचाई प्रणाली कैसे काम करती है?"
        ]
    else:
        prompts = [
            "What is the ideal soil moisture for tomatoes?",
            "How does the automated pump fail-safe work?",
            "How do I prevent fungal leaf blight?"
        ]

    for i, p in enumerate(prompts):
        if suggested_cols[i].button(p, key=f"sug_btn_{i}", use_container_width=True):
            suggested_query = p

    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])

    user_input = st.chat_input("Enter your agriculture related question...")
    if suggested_query:
        user_input = suggested_query

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
            
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        
        formatted_history = []
        assistant_messages = []
        for item in st.session_state.chat_history[:-1]:
            formatted_history.append({
                "role": "user" if item["role"] == "user" else "model",
                "text": item["text"]
            })
            if assistant_answer_question and AssistantMessage and item["role"] in ("user", "assistant"):
                assistant_messages.append(AssistantMessage(
                    role=item["role"],
                    content=item["text"]
                ))
            
        with st.chat_message("assistant"):
            with st.spinner("KrishiNidhi is thinking..."):
                reply = None
                if assistant_answer_question and AssistantRequest and lang_code in ("en", "te", "hi"):
                    try:
                        req_obj = AssistantRequest(
                            message=user_input,
                            language=lang_code,
                            history=assistant_messages[-10:]
                        )
                        reply = run_async(assistant_answer_question(req_obj))
                    except (AssistantUnavailable, Exception):
                        reply = None

                if not reply:
                    chat_req = ChatRequest(
                        message=user_input,
                        history=formatted_history,
                        language=chat_lang.split(" ")[0]
                    )
                    try:
                        reply = run_async(generate_chat_response(chat_req))
                    except Exception as chat_err:
                        reply = "I apologize, but I am unable to connect to the assistant services at the moment."
                
                st.write(reply)
                
        st.session_state.chat_history.append({"role": "assistant", "text": reply})
        st.rerun()

    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
        st.rerun()
