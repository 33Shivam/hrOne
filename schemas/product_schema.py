from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from typing import List

class SizeQuantity(BaseModel):
    size: str
    quantity: int


class ProductIn(BaseModel):
    name: str
    price: float
    sizes: List[SizeQuantity]

class ProductOut(ProductIn):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        fields = {"sizes": {"exclude": True}}


class ProductIDOut(BaseModel):
    id: str


class ProductResponseOut(BaseModel):
    id: str 
    name: str
    price: float


class PageInfo(BaseModel):
    next: Optional[str] = None
    limit: int
    previous: Optional[int] = None

class PaginatedProductResponse(BaseModel):
    data: List[ProductResponseOut]
    page: PageInfo

