# app/schemas/order_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OrderItem(BaseModel):
    productId: str = Field(description="Product ID")
    qty: int = Field(gt=0, description="Quantity must be greater than 0")

class OrderIn(BaseModel):
    user_id: str = Field(description="User identifier")
    items: List[OrderItem] = Field(min_items=1, description="Order items list")
    order_status: OrderStatus = OrderStatus.PLACED


class OrderOut(BaseModel):
    id: str = Field(description="Order ID")
    user_id: str
    items: List[OrderItem]
    order_status: OrderStatus
    total_amount: float = Field(description="Total order amount")
    created_at: datetime


class OrderIDOut(BaseModel):
    id: str = Field(description="Created order ID")


class PaginatedOrderResponse(BaseModel):
    data: List[OrderOut]
    page: dict
