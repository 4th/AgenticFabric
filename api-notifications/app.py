from fastapi import FastAPI
from common.telemetry import setup_tracing, instrument_fastapi
SERVICE = "api-notifications"
app = FastAPI(title=SERVICE); setup_tracing(SERVICE); instrument_fastapi(app, SERVICE)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception: pass
MESSAGES = []
@app.get("/healthz") def healthz(): return {"status":"ok","service":SERVICE}
@app.post("/notify") def notify(payload: dict):
    MESSAGES.append(payload); return {"status":"sent","count":len(MESSAGES)}
