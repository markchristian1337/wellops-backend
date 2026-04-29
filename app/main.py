from datetime import datetime, timezone
from fastapi import FastAPI
from app.api.routes import wells, alerts
from app.api.routes.sensors import temperatures
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WellOps Console API", version="0.1.0")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

app.include_router(wells.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(temperatures.router, prefix="/api")