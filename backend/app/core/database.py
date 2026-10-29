import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Determine if we are running in Streamlit Cloud
IS_STREAMLIT_CLOUD = (
    os.environ.get("STREAMLIT_SERVER_PORT") is not None 
    or "mount" in os.path.abspath(__file__) 
    or "home/adminuser" in os.path.abspath(__file__)
)

if IS_STREAMLIT_CLOUD:
    # Use relative path in the current working directory for Streamlit Cloud
    SQLALCHEMY_DATABASE_URL = "sqlite:///agritech.db"
else:
    # Local development - use absolute path to backend/agritech.db to share database state
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BACKEND_DIR = os.path.dirname(BASE_DIR)
    DB_PATH = os.path.join(BACKEND_DIR, "agritech.db")
    DB_PATH_CLEAN = DB_PATH.replace("\\", "/")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH_CLEAN}"


# connect_args={"check_same_thread": False} is needed only for SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Initializes database tables and ensures backwards-compatible schema
    upgrades (idempotent column additions) for SQLite databases.
    """
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(sensor_readings)"))
                existing_cols = {row[1] for row in result.fetchall()}
                if existing_cols:
                    cols_to_add = {
                        "device_id": "VARCHAR(64)",
                        "soil_moisture": "FLOAT",
                        "soil_raw": "INTEGER",
                        "motion_detected": "BOOLEAN DEFAULT 0",
                        "pump_on": "BOOLEAN DEFAULT 0",
                        "control_mode": "VARCHAR(16) DEFAULT 'AUTO'",
                    }
                    for col_name, col_type in cols_to_add.items():
                        if col_name not in existing_cols:
                            conn.execute(text(f"ALTER TABLE sensor_readings ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass


def get_db():
    """
    Dependency to be used in FastAPI routes to get a database session.
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
