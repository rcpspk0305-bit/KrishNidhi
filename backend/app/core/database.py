import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Compute standard absolute path to backend/agritech.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(BASE_DIR)
DEFAULT_DB_PATH = os.path.join(BACKEND_DIR, "agritech.db")

DATABASE_URL = os.environ.get("DATABASE_URL")
IS_STREAMLIT_CLOUD = (
    os.environ.get("STREAMLIT_SHARING_MODE") is not None
    or "mount" in os.path.abspath(__file__)
    or "home/adminuser" in os.path.abspath(__file__)
)

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
elif IS_STREAMLIT_CLOUD and not os.path.exists(DEFAULT_DB_PATH):
    # Fallback to local cwd sqlite on Streamlit Community Cloud container
    SQLALCHEMY_DATABASE_URL = "sqlite:///agritech.db"
else:
    # Local development & shared process - use absolute path to backend/agritech.db
    DB_PATH_CLEAN = DEFAULT_DB_PATH.replace("\\", "/")
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
