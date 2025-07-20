from fastapi import APIRouter, HTTPException, Depends , Query
from datetime import datetime
from bson import ObjectId
from typing import Optional, List

from ..db import products_collection
from ..schemas.product_schema import ProductIn, ProductOut , ProductIDOut , PaginatedProductResponse, PageInfo , ProductResponseOut
from ..utils.pagination import PageParams, apply_pagination

router = APIRouter(prefix="/products", tags=["Products"])

def fix_mongo_id(doc):
    """
    Safely convert MongoDB _id to id field
    """
    if not doc:
        return doc
    
    # Create a copy to avoid modifying the original
    result = doc.copy()
    
    if "_id" in result:
        result["id"] = str(result["_id"])
        result.pop("_id", None)  # Safely remove _id
    
    return result



@router.post("", response_model=ProductIDOut, status_code=201)
async def create_product(payload: ProductIn):
    doc = payload.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await products_collection.insert_one(doc)
    product_id = str(result.inserted_id)
    return ProductIDOut(id=product_id)


@router.get("", response_model=PaginatedProductResponse)
async def list_products(
    name: Optional[str] = Query(None, description="Partial/regex search on product name"),
    size: Optional[str] = Query(None, description="Filter products that include this size"),
    limit: int = Query(10, ge=1, le=100, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip for pagination")
):
    # Build MongoDB filter
    mongo_filter = {}
    if name:
        mongo_filter["name"] = {"$regex": name, "$options": "i"}
    if size:
        mongo_filter["sizes.size"] = size
    
    # Get total count for pagination calculation
    total_count = await products_collection.count_documents(mongo_filter)
    
    # Execute query with filters, sorting, and pagination
    cursor = (
        products_collection.find(mongo_filter)
        .sort("_id", 1)
        .skip(offset)
        .limit(limit)
    )
    
    products_raw = await cursor.to_list(length=limit)
    products_data = [ProductResponseOut(**fix_mongo_id(doc)) for doc in products_raw]
    
    # Calculate pagination info
    has_next = (offset + limit) < total_count
    has_previous = offset > 0
    
    page_info = PageInfo(
        next=str(offset + limit) if has_next else None,
        limit=len(products_data),  # Actual number returned
        previous=max(0, offset - limit) if has_previous else -10
    )
    
    return PaginatedProductResponse(
        data=products_data,
        page=page_info
    )



@router.get("/{prod_id}", response_model=ProductOut)
async def get_product(prod_id: str):
    doc = await products_collection.find_one({"_id": ObjectId(prod_id)})
    if not doc:
        raise HTTPException(404, "Product not found")
    return ProductOut(**fix_mongo_id(doc))
