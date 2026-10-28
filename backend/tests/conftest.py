import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.core.security import hash_api_key
from app.models.db_models import Device, PlantProfile

# In-memory SQLite for high-speed, isolated test execution
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def seeded_device(db_session):
    raw_key = "test_secret_key_123"
    dev = Device(
        id="esp8266-test-unit",
        name="Test ESP8266 Unit",
        api_key_hash=hash_api_key(raw_key),
        status="online",
        control_mode="AUTO",
        pump_state=False,
    )
    db_session.add(dev)
    db_session.flush()

    profile = PlantProfile(
        device_id=dev.id,
        plant_name="Test Plant",
        plant_type="Vegetable",
        preferred_temp_min=18.0,
        preferred_temp_max=30.0,
        preferred_humidity_min=50.0,
        preferred_humidity_max=70.0,
        preferred_moisture_min=30.0,
        preferred_moisture_max=60.0,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(dev)
    return {"device": dev, "api_key": raw_key}
