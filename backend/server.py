import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Export full production-quality FastAPI application with DB persistence, SSE, CORS, and full device API
from app.main import app

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting Plant Health Monitoring API on {host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

