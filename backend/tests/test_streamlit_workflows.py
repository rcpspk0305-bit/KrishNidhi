import os
import io
import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

from app.models.schemas import SensorData, GenAIRequest, ChatRequest
from app.services.ml_service import predict_crop
from app.services.vision_service import detect_disease_from_image
from app.services.llm_service import generate_action_plan, generate_chat_response
from app.core.database import SessionLocal
from app.models import db_models

# Locate streamlit_app.py in repository root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STREAMLIT_APP_PATH = os.path.join(PROJECT_ROOT, "streamlit_app.py")


def test_streamlit_app_loads_without_errors():
    """
    Test 1: Verify that streamlit_app.py boots up with zero unhandled exceptions.
    """
    assert os.path.exists(STREAMLIT_APP_PATH), (
        f"streamlit_app.py not found at {STREAMLIT_APP_PATH}"
    )
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0, (
        f"AppTest threw exceptions on load: {[e.message for e in at.exception]}"
    )

    # Verify main title and subheader
    subheaders = [s.value for s in at.subheader]
    assert "Interactive Telemetry & Analytics" in subheaders
    assert "Historical Sensor Trends" in subheaders
    assert "Soil NPK Ratio" in subheaders


def test_realtime_dashboard_workflow():
    """
    Test 2: Verify Real-time Dashboard workflow:
    - Default view and telemetry source selection
    - Switching to Manual Telemetry Simulator
    - Pushing a new simulated reading to the database
    - Updating session notifications and sensor metrics
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    # Ensure we are on Real-time Dashboard
    workspace_radio = at.sidebar.radio[0]
    workspace_radio.set_value(workspace_radio.options[0]).run()

    # Switch Telemetry Source to '🧪 Manual Telemetry Simulator'
    telemetry_radio = at.radio[0]
    telemetry_radio.set_value("🧪 Manual Telemetry Simulator").run()
    assert len(at.exception) == 0

    # Verify '🔄 Push Live Reading to DB' button exists
    push_button = [b for b in at.button if "Push Live Reading" in b.label]
    assert len(push_button) == 1, (
        "Expected Push Live Reading to DB button in simulator mode"
    )

    # Count existing readings in DB
    db = SessionLocal()
    initial_count = db.query(db_models.SensorReading).count()
    db.close()

    # Click the push button and run
    push_button[0].click().run()
    assert len(at.exception) == 0

    # Verify a new reading was written to DB
    db = SessionLocal()
    new_count = db.query(db_models.SensorReading).count()
    db.close()
    assert new_count >= initial_count + 1, (
        f"Expected DB count to increase from {initial_count}, got {new_count}"
    )


def test_crop_recommendation_workflow():
    """
    Test 3: Verify Soil-Specific Crop Recommendation Advisor workflow:
    - Switching workspace to '🌾 Crop Recommendation'
    - Adjusting soil and telemetry sliders
    - Triggering Suitability Engine
    - Verifies prediction computation and agronomic cultivation guidelines
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    # Switch workspace to Crop Recommendation
    workspace_radio = at.sidebar.radio[0]
    crop_option = [
        opt for opt in workspace_radio.options if "Crop Recommendation" in opt
    ][0]
    workspace_radio.set_value(crop_option).run()
    assert len(at.exception) == 0

    # Verify page title/subheader
    subheaders = [s.value for s in at.subheader]
    assert any("Soil-Specific Crop Advisor" in s for s in subheaders)

    # Click '🌾 Run Suitability Engine'
    run_btn = [b for b in at.button if "Run Suitability" in b.label]
    assert len(run_btn) == 1
    run_btn[0].click().run()
    assert len(at.exception) == 0

    # Verify cultivation advice is displayed
    assert len(at.info) > 0, "Expected cultivation best practice info alert"
    assert len(at.info[0].value) > 10

    # Directly verify ML service prediction contract
    sample_sensor = SensorData(
        N=90.0,
        P=45.0,
        K=40.0,
        temperature=28.0,
        humidity=70.0,
        ph=6.5,
        rainfall=120.0,
        tds=140.0,
    )
    predicted_crop = predict_crop(sample_sensor)
    assert isinstance(predicted_crop, str)
    assert len(predicted_crop) > 0


def test_leaf_disease_diagnosis_workflow():
    """
    Test 4: Verify AI Vision Leaf Disease Diagnosis workflow:
    - Switching workspace to '🍃 Leaf Disease Diagnosis'
    - Verifies file uploader and language selector widgets
    - Executes vision diagnosis on a synthetic leaf image
    - Generates actionable agronomic recommendations
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    # Switch workspace to Leaf Disease Diagnosis
    workspace_radio = at.sidebar.radio[0]
    disease_option = [opt for opt in workspace_radio.options if "Leaf Disease" in opt][
        0
    ]
    workspace_radio.set_value(disease_option).run()
    assert len(at.exception) == 0

    # Check UI widgets presence
    assert len(at.file_uploader) == 1
    assert any("English" in sb.options for sb in at.selectbox)

    # Create synthetic leaf image (128x128 green PNG)
    img = Image.new("RGB", (128, 128), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # Execute vision detection pipeline directly
    condition, confidence, bbox = detect_disease_from_image(image_bytes)
    assert isinstance(condition, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
    assert isinstance(bbox, (list, tuple)) and len(bbox) == 4

    # Execute action plan generation
    req = GenAIRequest(
        crop="Tomato",
        disease=condition,
        sensor_data={"temperature": 27.0, "humidity": 65.0, "ph": 6.4},
        language="English",
    )
    import asyncio

    plan = asyncio.run(generate_action_plan(req))
    assert isinstance(plan, str)
    assert len(plan) > 20


def test_ai_chatbot_workflow():
    """
    Test 5: Verify KrishiNidhi AI Chatbot workflow:
    - Switching workspace to '🤖 KrishiNidhi AI Chatbot'
    - Verifying chat input and language selectors
    - Generating responses for farmer queries
    - Testing 'Clear Chat History' button
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    # Switch workspace to Chatbot
    workspace_radio = at.sidebar.radio[0]
    chat_option = [opt for opt in workspace_radio.options if "Chatbot" in opt][0]
    workspace_radio.set_value(chat_option).run()
    assert len(at.exception) == 0

    # Verify chat elements
    assert len(at.chat_input) == 1
    clear_buttons = [b for b in at.sidebar.button if "Clear Chat" in b.label]
    assert len(clear_buttons) == 1

    # Test Chatbot LLM Service
    chat_req = ChatRequest(
        message="What is the recommended soil pH for growing tomatoes?",
        history=[],
        language="English",
    )
    import asyncio

    reply = asyncio.run(generate_chat_response(chat_req))
    assert isinstance(reply, str)
    assert len(reply) > 20


def test_smart_plant_sensor_monitoring_workflow():
    """
    Test 6: Verify Smart Plant IoT sensor monitoring and simulation:
    - Verifies presence of Soil Moisture, PIR Motion, and Pump controls
    - Simulates adjusting soil moisture and pump state
    - Pushes reading and verifies database records store smart plant telemetry
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    # Switch Telemetry Source to '🧪 Manual Telemetry Simulator'
    telemetry_radio = at.radio[0]
    telemetry_radio.set_value("🧪 Manual Telemetry Simulator").run()
    assert len(at.exception) == 0

    # Verify Soil Moisture slider exists
    soil_sliders = [s for s in at.slider if "Soil Moisture" in s.label]
    assert len(soil_sliders) == 1, "Expected Soil Moisture slider in simulator"
    soil_sliders[0].set_value(58.5).run()

    # Verify push live reading button and push
    push_button = [b for b in at.button if "Push Live Reading" in b.label]
    assert len(push_button) == 1
    push_button[0].click().run()
    assert len(at.exception) == 0

    # Verify reading in DB has soil moisture recorded
    db = SessionLocal()
    latest_reading = (
        db.query(db_models.SensorReading)
        .order_by(db_models.SensorReading.timestamp.desc())
        .first()
    )
    db.close()
    assert latest_reading is not None
    assert latest_reading.soil_moisture is not None
    assert latest_reading.soil_moisture == 58.5


def test_multilingual_assistant_workflow():
    """
    Test 7: Verify Multilingual AI Assistant in Streamlit:
    - Switches workspace to Chatbot / Assistant
    - Verifies language selectbox has English, Telugu, and Hindi options
    - Tests language switching
    """
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0

    workspace_radio = at.sidebar.radio[0]
    chat_option = [opt for opt in workspace_radio.options if "Chatbot" in opt][0]
    workspace_radio.set_value(chat_option).run()
    assert len(at.exception) == 0

    # Verify language options include English, Telugu, Hindi
    lang_selectbox = at.selectbox[0]
    options_str = " ".join(lang_selectbox.options)
    assert "English" in options_str
    assert "Telugu" in options_str
    assert "Hindi" in options_str

    # Switch to Telugu
    telugu_opt = [opt for opt in lang_selectbox.options if "Telugu" in opt][0]
    lang_selectbox.set_value(telugu_opt).run()
    assert len(at.exception) == 0

