from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class OrderItem(BaseModel):
    sku: str
    qty: int = Field(ge=1)
    price: float = Field(ge=0)

class Order(BaseModel):
    id: Optional[str] = None
    user_id: str
    items: List[OrderItem]
    total: float = 0.0
    status: str = "PENDING"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Payment(BaseModel):
    id: Optional[str] = None
    order_id: str
    amount: float
    method: str = "card"
    status: str = "INITIATED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InventoryItem(BaseModel):
    sku: str
    name: str
    stock: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(BaseModel):
    to: str
    subject: str
    body: str

class ActRequest(BaseModel):
    goal: str
    inputs: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None

class ActResponse(BaseModel):
    plan: list
    result: Dict[str, Any]
