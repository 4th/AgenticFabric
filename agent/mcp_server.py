from __future__ import annotations
import os, json, typing as t
import httpx
from mcp.server.fastmcp import FastMCP

ORDERS_URL        = os.getenv("ORDERS_URL", "http://api-orders:8000")
PAYMENTS_URL      = os.getenv("PAYMENTS_URL", "http://api-payments:8000")
INVENTORY_URL     = os.getenv("INVENTORY_URL", "http://api-inventory:8000")
NOTIFICATIONS_URL = os.getenv("NOTIFY_URL", "http://api-notifications:8000")
MEMORY_URL        = os.getenv("MEMORY_URL", "http://agentfabric:8000")

mcp = FastMCP("AgentFabric-MCP")

@mcp.tool()
async def create_order(user_id: str, items: list[dict], notes: str | None = None) -> dict:
    """Create an order in the Orders API."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{ORDERS_URL}/orders", json={"user_id": user_id, "items": items, "notes": notes})
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def charge_payment(order_id: str, amount: float, method: str = "card") -> dict:
    """Charge a payment for an order in the Payments API."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{PAYMENTS_URL}/payments", json={"order_id": order_id, "amount": amount, "method": method})
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def adjust_inventory(sku: str, delta: int) -> dict:
    """Adjust inventory for a SKU (positive = add; negative = reduce)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.patch(f"{INVENTORY_URL}/items/{sku}", json={"stock": delta})
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def send_notification(to: str, subject: str, body: str) -> dict:
    """Send a notification via the Notifications API."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{NOTIFICATIONS_URL}/notify", json={"to": to, "subject": subject, "body": body})
        r.raise_for_status()
        return r.json()

@mcp.resource("inventory://{sku}")
async def get_inventory(sku: str) -> str:
    """Read inventory record for a SKU (demo)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{INVENTORY_URL}/items")
        r.raise_for_status()
        items = r.json()
        for it in items:
            if it.get("sku") == sku:
                return json.dumps(it, ensure_ascii=False)
        return json.dumps({"error": "not found", "sku": sku}, ensure_ascii=False)

@mcp.resource("orders://recent")
async def recent_orders() -> str:
    """Read recent orders (demo)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{ORDERS_URL}/orders")
        r.raise_for_status()
        return json.dumps(r.json(), ensure_ascii=False)

@mcp.resource("memory://recent")
async def recent_memory() -> str:
    """Expose recent in-proc agent memory (if available)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{MEMORY_URL}/agent/memory/recent?n=10")
            r.raise_for_status()
            return r.text
    except Exception:
        return "No memory endpoint configured."

@mcp.prompt()
def order_triage(issue: str, order_json: str) -> str:
    """Template prompt for safe order triage."""
    return (
        "You are an order-triage assistant. Follow policy; never leak secrets; "
        "prefer refunds/credits per policy. Issue:\n"
        f"{issue}\n\nOrder JSON:\n{order_json}\n\n"
        "Decide: REFUND|CREDIT|ESCALATE and provide rationale and next steps."
    )

if __name__ == "__main__":
    # mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")
