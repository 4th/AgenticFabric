from fastapi import FastAPI
from common.telemetry import setup_tracing, instrument_fastapi
SERVICE = "api-orders"
app = FastAPI(title=SERVICE); setup_tracing(SERVICE); instrument_fastapi(app, SERVICE)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception: pass
ORDERS = []
@app.get("/healthz") def healthz(): return {"status":"ok","service":SERVICE}
@app.get("/orders") def list_orders(): return ORDERS
@app.post("/orders") def create_order(order: dict):
    order.setdefault("id", f"ord-{len(ORDERS)+1}"); ORDERS.append(order); return order
