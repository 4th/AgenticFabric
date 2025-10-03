# AgentFabric (MCP-enabled)

- MCP HTTP endpoint: `http://localhost:8000/mcp`
- Try locally:
  ```bash
  uvicorn agent.app:app --host 0.0.0.0 --port 8000
  mcp dev agent/mcp_server.py
  ```
