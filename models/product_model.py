from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ProductIn(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    size: str

class ProductOut(ProductIn):
    id: str = Field(alias="_id")
    created_at: datetime
