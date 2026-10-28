import streamlit as st
import sys
import os
import random
import asyncio
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

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
    count = db.query(db_models.SensorReading).count()
    if count == 0:
        now = datetime.utcnow()
        for i in range(24, 0, -1):
            timestamp = now - pd.Timedelta(hours=i)
            reading = db_models.SensorReading(
                timestamp=timestamp,
                temperature=round(25.5 + random.uniform(-2, 2), 1),
                humidity=round(40.0 + random.uniform(-5, 5), 1),
                ph=round(6.8 + random.uniform(-0.2, 0.2), 2),
                rainfall=round(50.0 + random.uniform(-10, 10), 1),
                n=round(88.0 + random.uniform(-5, 5), 1),
                p=round(50.0 + random.uniform(-3, 3), 1),
                k=round(42.0 + random.uniform(-3, 3), 1),
                tds=round(150.0 + random.uniform(-15, 15), 1)
            )
            db.add(reading)
        db.commit()

db = get_db()
populate_initial_data(db)

# Streamlit Page Config
st.set_page_config(
    page_title="KrishiNidhi - Smart AgriTech Portal",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Dark-Violet Aesthetics
st.markdown("""
<style>
    /* Dark Violet Gradient Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0512 0%, #150a21 50%, #05020a 100%);
        color: #e2d9eb;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 5, 18, 0.96) !important;
        border-right: 1px solid rgba(138, 43, 226, 0.2);
    }
    
    /* Hide top Streamlit elements */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Custom Headers */
    .title-banner {
        background: linear-gradient(90deg, #9932cc 0%, #da70d6 50%, #8a2be2 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(138, 43, 226, 0.3);
        margin-bottom: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .main-title {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .sub-title {
        color: #cbb4e6;
        font-size: 1.1rem;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 300;
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(30, 16, 48, 0.4);
        border: 1px solid rgba(138, 43, 226, 0.25);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #b19cd9;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .card-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: inline-block;
    }
    .card-unit {
        font-size: 1rem;
        color: #da70d6;
        margin-left: 4px;
        display: inline-block;
    }
    .card-hint {
        font-size: 0.78rem;
        color: #00ffc4;
        margin-top: 6px;
    }
    
    /* Interactive elements */
    .stButton>button {
        background: linear-gradient(135deg, #8a2be2 0%, #da70d6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(218, 112, 214, 0.6) !important;
    }
    
    /* Custom alerts */
    .notification-item {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #da70d6;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
    }
    
    .badge {
        background: rgba(138, 43, 226, 0.2);
        color: #e0b0ff;
        border: 1px solid rgba(138, 43, 226, 0.4);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Application Top Banner
st.markdown("""
<div class="title-banner">
    <span class="badge">🌱 AgriTech Operations Control Center</span>
    <h1 class="main-title">KrishiNidhi</h1>
    <h3 class="sub-title">Advanced Machine Learning & Generative AI Dashboard</h3>
</div>
""", unsafe_allow_html=True)

# Navigation / Sidebar config
st.sidebar.markdown("<h2 style='color:#e2d9eb; margin-bottom:20px; font-weight:700;'>Navigation</h2>", unsafe_allow_html=True)
app_mode = st.sidebar.radio(
    "Select Workspace",
    ["📊 Real-time Dashboard", "🌾 Crop Recommendation", "🍃 Leaf Disease Diagnosis", "🤖 KrishiNidhi AI Chatbot"]
)

# Shared Status in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#b19cd9;'>System Config</h3>", unsafe_allow_html=True)

# Display Key Configuration Statuses
has_gemini = "Configured" if settings.GEMINI_API_KEY else "Missing (Using Fallbacks)"
has_twilio = "Configured" if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN else "Missing"
st.sidebar.markdown(f"**Gemini GenAI:** {has_gemini}")
st.sidebar.markdown(f"**Twilio SMS Alerting:** {has_twilio}")

# Active alerts container helper
def add_notification(text):
    if "notifications" not in st.session_state:
        st.session_state.notifications = [
            "Soil moisture dipped 4% from the previous reading.",
            "Water TDS is inside safe irrigation range.",
            "Predicted crop fit remains stable for the next 6-hour window."
        ]
    st.session_state.notifications.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
    if len(st.session_state.notifications) > 6:
        st.session_state.notifications.pop()

if "notifications" not in st.session_state:
    st.session_state.notifications = [
        "[20:45:01] Soil moisture dipped 4% from the previous reading.",
        "[20:30:12] Water TDS is inside safe irrigation range.",
        "[20:00:00] Predicted crop fit remains stable for the next 6-hour window."
    ]

# ----------------- TABS / SCREEN DEFINITIONS -----------------

if app_mode == "📊 Real-time Dashboard":
    st.subheader("Interactive Telemetry & Analytics")
    
    # Telemetry source selector
    telemetry_mode = st.radio(
        "Telemetry Source",
        ["🛰️ Real-World Live IoT Stream", "🧪 Manual Telemetry Simulator"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if telemetry_mode == "🛰️ Real-World Live IoT Stream":
        is_live = iot_metadata.get("connected", False)
        last_pkt = iot_metadata.get("last_packet_time")
        status_color = "#00ffc4" if is_live else "#fbbf24"
        status_text = "HARDWARE LIVE & TRANSMITTING" if is_live else "WAITING FOR HARDWARE TELEMETRY"
        dev_id = iot_metadata.get("device_id", "esp32-node-01")
        source_name = iot_metadata.get("source", "standby").upper()
        pkt_cnt = iot_metadata.get("packet_count", 0)

        col_badge, col_sync = st.columns([3, 1])
        with col_badge:
            st.markdown(f"""
            <div style="background: rgba(18, 22, 38, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {status_color}; border-radius: 12px; padding: 12px 18px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {status_color}; margin-right: 6px; box-shadow: 0 0 8px {status_color};"></span>
                        <b style="color: {status_color}; font-size: 0.85rem; letter-spacing: 0.05em;">{status_text}</b>
                        <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 8px;">| Device: <code style="color: #60a5fa;">{dev_id}</code></span>
                        <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 8px;">| Source: <span style="color: #c084fc;">{source_name}</span></span>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">
                        Packets: <b style="color: white;">{pkt_cnt}</b> | Last Seen: <b style="color: white;">{last_pkt[-8:] if last_pkt else 'Never'}</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_sync:
            if st.button("🔄 Sync Telemetry", use_container_width=True):
                st.rerun()

        with st.expander("🔌 Quick Hardware Ingestion & Terminal Test Command"):
            st.markdown("""
            **1. HTTP Ingestion Endpoint (POST):**
            ```bash
            curl -X POST http://localhost:8000/iot/telemetry -H "Content-Type: application/json" -d '{"device_id": "esp32-field-01", "temperature": 28.4, "humidity": 65.0, "ph": 6.8, "N": 92, "P": 48, "K": 45, "rainfall": 55.0, "tds": 145}'
            ```
            **2. MQTT Ingestion Broker:**
            - **Broker**: `broker.hivemq.com:1883`
            - **Topic**: `agritech/ps10/sensors`
            - **Sample JSON**: `{"device_id": "esp32-node-01", "temperature": 27.5, "humidity": 60, "ph": 6.5, "N": 85, "P": 50, "K": 40}`
            - **Firmware code**: Check `iot/esp32/esp32_mqtt.ino` and `iot/esp32/sensor_readings.ino`.
            """)
    else:
        # Simulate data controls
        col_ctr, col_state = st.columns([2, 1])
        with col_ctr:
            st.write("Adjust sensor sliders to test live ML recommendations and dashboard graphs.")
            
        with col_state:
            # Save simulated data button
            if st.button("🔄 Push Live Reading to DB"):
                db = get_db()
                new_reading = db_models.SensorReading(
                    temperature=latest_iot_data["temperature"],
                    humidity=latest_iot_data["humidity"],
                    ph=latest_iot_data["ph"],
                    rainfall=latest_iot_data["rainfall"],
                    n=latest_iot_data["N"],
                    p=latest_iot_data["P"],
                    k=latest_iot_data["K"],
                    tds=latest_iot_data["tds"]
                )
                db.add(new_reading)
                db.commit()
                add_notification(f"Manual telemetry reading written. Temp: {latest_iot_data['temperature']}°C")
                st.success("Reading successfully pushed to Database!")
                st.rerun()

        # Create sliders for real-time adjustments
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

    st.markdown("---")

    # Metrics Section
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Temperature</div>
            <div class="card-value">{latest_iot_data['temperature']}</div>
            <div class="card-unit">°C</div>
            <div class="card-hint">Optimal: 20-30°C</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Humidity</div>
            <div class="card-value">{latest_iot_data['humidity']}</div>
            <div class="card-unit">%</div>
            <div class="card-hint">Optimal: 40-70%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Soil pH</div>
            <div class="card-value">{latest_iot_data['ph']}</div>
            <div class="card-unit">pH</div>
            <div class="card-hint">Optimal: 6.0-7.5</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Water TDS</div>
            <div class="card-value">{latest_iot_data.get('tds', 150.0)}</div>
            <div class="card-unit">ppm</div>
            <div class="card-hint">Optimal: &lt; 200 ppm</div>
        </div>
        """, unsafe_allow_html=True)

    # Main Visual Analytics
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Historical Sensor Trends")
        # Load historical readings from database
        db = get_db()
        readings = db.query(db_models.SensorReading).order_by(db_models.SensorReading.timestamp.desc()).limit(30).all()
        
        if readings:
            data_list = []
            for r in reversed(readings):
                data_list.append({
                    "Timestamp": r.timestamp,
                    "Temperature (°C)": r.temperature,
                    "Humidity (%)": r.humidity,
                    "pH": r.ph,
                    "Rainfall (mm)": r.rainfall,
                    "Nitrogen": r.n,
                    "Phosphorus": r.p,
                    "Potassium": r.k
                })
            df = pd.DataFrame(data_list)
            
            # Multi-series plot
            fig = px.line(
                df, 
                x="Timestamp", 
                y=["Temperature (°C)", "Humidity (%)", "Rainfall (mm)"],
                title="Soil Temperature, Moisture, & Rain Trends",
                color_discrete_sequence=["#8a2be2", "#da70d6", "#00ffc4"]
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#e2d9eb",
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical readings found in database.")

    with col_right:
        # NPK Distribution Bar Chart
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
                "Nitrogen (N)": "#8a2be2",
                "Phosphorus (P)": "#da70d6",
                "Potassium (K)": "#00ffc4"
            }
        )
        fig_npk.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#e2d9eb",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
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
        <div class="glass-card" style="border-color: rgba(0, 255, 196, 0.4)">
            <h4 style="margin-top: 0; color: #00ffc4;">🌱 Live ML Model Output</h4>
            <p style="margin-bottom: 4px; font-size: 0.9rem;">Recommended Crop for Current Soil/Telemetry:</p>
            <h2 style="color: #ffffff; margin-top: 4px; font-size: 2.2rem; font-weight: 800;">{rec_crop}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Notification logger
        st.markdown("### Operator Notifications Logs")
        for log in st.session_state.notifications:
            st.markdown(f'<div class="notification-item">{log}</div>', unsafe_allow_html=True)

# ----------------- CROP RECOMMENDATION MODULE -----------------

elif app_mode == "🌾 Crop Recommendation":
    st.subheader("Soil-Specific Crop Advisor Sandbox")
    st.write("Tune the parameters below to compute crop suitability recommendations using the ML model.")

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
        <div class="glass-card" style="border-left: 5px solid #8a2be2; background: rgba(138, 43, 226, 0.05);">
            <h4 style="margin: 0; color: #b19cd9; text-transform: uppercase; font-size: 0.8rem; letter-spacing:0.1em;">Engine Prediction Match</h4>
            <h1 style="color: #ffffff; margin-top: 10px; margin-bottom: 12px; font-weight:800; font-size: 3rem;">{rec}</h1>
            <p style="color: #e2d9eb; margin-bottom: 0; font-size: 0.95rem;">
                Based on Nitrogen level of <b>{N}</b>, soil acidity pH <b>{ph}</b>, humidity <b>{hum}%</b> and rainfall of <b>{rain}mm</b>, 
                the model suggests cultivating <b>{rec}</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Details about crops
        st.subheader("Cultivation Best Practices")
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

# ----------------- LEAF DISEASE DIAGNOSIS (VISION) -----------------

elif app_mode == "🍃 Leaf Disease Diagnosis":
    st.subheader("AI Vision Disease Detector")
    st.write("Upload a picture of a crop leaf to identify diseases and generate a tailored agronomic action plan.")

    # Image upload widgets
    uploaded_file = st.file_uploader("Upload Leaf Snapshot (JPEG/PNG)", type=["jpg", "jpeg", "png"])
    
    # Lang selector for action plan translation
    language = st.selectbox("Preferred Communication Language", ["English", "Telugu", "Hindi", "Spanish", "French"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col_img, col_diag = st.columns([1, 1])
        
        with col_img:
            st.image(image, caption="Uploaded Crop Image", use_container_width=True)
            
        with col_diag:
            st.markdown("### Analysis Pipeline")
            
            with st.spinner("Analyzing image features via Gemini..."):
                # Get raw byte content of image
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                
                # Execute detection
                disease, confidence, bbox = detect_disease_from_image(image_bytes)
                
            st.success("Diagnosis Complete!")
            st.markdown(f"""
            <div class="glass-card" style="border-left: 5px solid #00ffc4; background: rgba(0, 255, 196, 0.03);">
                <h5 style="margin: 0; color: #00ffc4; text-transform: uppercase;">Condition Identified</h5>
                <h2 style="color: white; margin-top: 6px; font-weight: 700;">{disease}</h2>
                <p style="margin: 0; color: #b19cd9;">Confidence: <b>{confidence*100:.1f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action plan generator
            st.markdown("### Agronomic Action Plan")
            with st.spinner("Generating Action Plan..."):
                # Call async action plan generator via asyncio
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
            
            # Twilio SMS Alert section
            st.markdown("---")
            st.markdown("### SMS Operator Dispatcher")
            st.write("Send this diagnosis and plan to the field operator's phone.")
            
            target_phone = st.text_input("Operator Phone Number", value=settings.TWILIO_TO_NUMBER or "+1234567890")
            
            if st.button("📲 Dispatch SMS Alert"):
                if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                    st.warning("Twilio is not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in `.env`.")
                else:
                    with st.spinner("Sending message..."):
                        try:
                            from twilio.rest import Client
                            # Generate a short prompt for translations
                            prompt = f"""
                            You are an expert translator. Summarize this agricultural action plan in 1 short sentence in English, and then provide the exact translation in {language}.
                            Disease: {disease}
                            Plan: {action_plan}
                            
                            Format exactly like this:
                            [EN] <english sentence>
                            [{language[:2].upper()}] <translated sentence>
                            """
                            
                            sms_body = f"Alert: {disease} detected."
                            if client_model:
                                resp = client_model.models.generate_content(
                                    model="gemini-1.5-flash",
                                    contents=prompt
                                )
                                if resp.text:
                                    sms_body = resp.text.strip()
                            
                            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            message = client.messages.create(
                                body=f"KrishiNidhi Alert:\n{sms_body}",
                                from_=settings.TWILIO_FROM_NUMBER,
                                to=target_phone
                            )
                            st.success(f"SMS successfully dispatched! Message SID: {message.sid}")
                            add_notification(f"SMS Alert sent to {target_phone} for {disease}")
                        except Exception as ex:
                            st.error(f"Failed to dispatch SMS: {ex}")

# ----------------- KRISHINIDHI AI CHATBOT -----------------

elif app_mode == "🤖 KrishiNidhi AI Chatbot":
    st.subheader("KrishiNidhi Agronomist Assistant")
    st.write("Ask agricultural questions. The chatbot leverages Gemini with a local fallback PDF RAG (using the agriculture-compendium.pdf).")
    
    chat_lang = st.selectbox("Preferred Chat Language", ["English", "Telugu", "Hindi", "Spanish"])
    
    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display prior messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])

    # User chat input
    user_input = st.chat_input("Enter your agriculture related question...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
            
        # Append user message to history
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        
        # Prepare historical requests
        formatted_history = []
        for item in st.session_state.chat_history[:-1]:
            formatted_history.append({
                "role": "user" if item["role"] == "user" else "model",
                "text": item["text"]
            })
            
        # Generate chatbot reply
        with st.chat_message("assistant"):
            with st.spinner("KrishiNidhi is thinking..."):
                chat_req = ChatRequest(
                    message=user_input,
                    history=formatted_history,
                    language=chat_lang
                )
                try:
                    # Run async chat response generator
                    reply = run_async(generate_chat_response(chat_req))
                except Exception as chat_err:
                    st.error(f"Chat generation error: {chat_err}")
                    reply = "I apologize, but I am unable to connect to the assistant services at the moment."
                
                st.write(reply)
                
        # Append response to history
        st.session_state.chat_history.append({"role": "assistant", "text": reply})
        
        # Clear/Rerun to keep layouts matching
        st.rerun()

    # Clear chat session
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
        st.rerun()
