from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

## OrderItem schemas (define these first so Order schemas can reference them)
class OrderItemCreate(BaseModel):
    offer_id: int
    quantity: int

class OrderItemResponse(BaseModel):
    id: int
    offer_id: int
    quantity: int
    order_id: int

    model_config = {"from_attributes": True}

## Order schemas
class OrderCreate(BaseModel):
    user_id: str
    partner_id: str
    items: List[OrderItemCreate]
    amount: Decimal | None = None

class OrderResponse(BaseModel):
    id: int
    user_id: str
    order_status: str
    payment_status: str
    payment_id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
    external_id: Optional[str]

    model_config = {"from_attributes": True}

class OrderPaymentUpdate(BaseModel):
    payment_id: int
    payment_status: str

