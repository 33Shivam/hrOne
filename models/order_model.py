from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class OrderIn(BaseModel):
    user_id: str
    product_ids: List[str] = Field(min_items=1)
    order_status: str = "PLACED"

class OrderOut(OrderIn):
    id: str = Field(alias="_id")
    created_at: datetime
