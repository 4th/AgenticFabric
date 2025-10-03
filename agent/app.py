from fastapi import FastAPI, Query
from .mcp_server import mcp

app = FastAPI(title="AgentFabric Orchestrator")

# MCP at /mcp (HTTP transport)
app.mount("/mcp", mcp.streamable_http_app())

# Minimal memory endpoint for MCP demo
_recent = []

@app.get("/agent/memory/recent")
def memory_recent(n: int = Query(10, ge=1, le=100)):
    return _recent[-n:]

@app.get("/healthz")
def healthz():
    return {"status":"ok"}
