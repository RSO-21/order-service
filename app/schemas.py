from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import List

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
    user_id: int
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_status: str
    payment_status: str
    payment_id: int | None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    model_config = {"from_attributes": True}

