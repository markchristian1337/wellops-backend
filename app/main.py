from datetime import datetime, timezone
from fastapi import FastAPI
from app.api.routes import wells, alerts

app = FastAPI(title="WellOps Console API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

app.include_router(wells.router)
app.include_router(alerts.router)
