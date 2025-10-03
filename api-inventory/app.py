from fastapi import FastAPI, HTTPException
from common.telemetry import setup_tracing, instrument_fastapi
SERVICE = "api-inventory"
app = FastAPI(title=SERVICE); setup_tracing(SERVICE); instrument_fastapi(app, SERVICE)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception: pass
ITEMS = [{"sku":"SKU-1","name":"Widget","stock":100},{"sku":"SKU-2","name":"Gadget","stock":50}]
@app.get("/healthz") def healthz(): return {"status":"ok","service":SERVICE}
@app.get("/items") def list_items(): return ITEMS
@app.patch("/items/{sku}") def update_stock(sku: str, patch: dict):
    for it in ITEMS:
        if it["sku"]==sku: it.update(patch); return it
    raise HTTPException(status_code=404, detail="Not found")
