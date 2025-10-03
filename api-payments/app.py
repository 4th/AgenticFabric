from fastapi import FastAPI
from common.telemetry import setup_tracing, instrument_fastapi
SERVICE = "api-payments"
app = FastAPI(title=SERVICE); setup_tracing(SERVICE); instrument_fastapi(app, SERVICE)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception: pass
PAYMENTS = []
@app.get("/healthz") def healthz(): return {"status":"ok","service":SERVICE}
@app.post("/payments") def make_payment(payment: dict):
    payment.setdefault("id", f"pay-{len(PAYMENTS)+1}"); payment.setdefault("status","APPROVED")
    PAYMENTS.append(payment); return payment
