# app/routers/orders.py
from fastapi import APIRouter, HTTPException, Depends , Query
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from ..db import orders_collection, products_collection
from ..schemas.order_schema import OrderIn, OrderOut, OrderIDOut , PaginatedOrderResponse
from ..utils.pagination import PageParams, apply_pagination

router = APIRouter(prefix="/orders", tags=["Orders"])

def fix_order_ids(doc):
    """Convert ObjectId fields to strings for API response"""
    if not doc:
        return doc
    
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    
    # Ensure items have string productIds
    if "items" in doc:
        for item in doc["items"]:
            if "productId" in item and hasattr(item["productId"], '__str__'):
                item["productId"] = str(item["productId"])
    
    return doc

async def validate_products_and_calculate_total(items: List[dict]) -> tuple[bool, float, str]:
    """
    Validate products exist and calculate total amount
    Returns: (is_valid, total_amount, error_message)
    """
    total_amount = 0.0
    product_ids = [ObjectId(item["productId"]) for item in items]
    
    # Fetch all products in one query
    products_cursor = products_collection.find({"_id": {"$in": product_ids}})
    products = {str(product["_id"]): product async for product in products_cursor}
    
    # Validate each item
    for item in items:
        product_id = item["productId"]
        
        if product_id not in products:
            return False, 0.0, f"Product {product_id} not found"
        
        product = products[product_id]
        item_total = product["price"] * item["qty"]
        total_amount += item_total
    
    return True, round(total_amount, 2), ""

@router.post("", response_model=OrderIDOut, status_code=201)
async def create_order(order: OrderIn):
    """Create a new order"""
    
    # Convert items to dict format
    items_dict = [item.dict() for item in order.items]
    
    # Validate products exist and calculate total
    is_valid, total_amount, error_msg = await validate_products_and_calculate_total(items_dict)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Prepare order document
    order_doc = {
        "user_id": order.user_id,
        "items": [
            {
                "productId": ObjectId(item["productId"]),
                "qty": item["qty"]
            }
            for item in items_dict
        ],
        "order_status": order.order_status,
        "total_amount": total_amount,
        "created_at": datetime.utcnow()
    }
    
    try:
        result = await orders_collection.insert_one(order_doc)
        return OrderIDOut(id=str(result.inserted_id))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/{user_id}")
async def get_user_orders(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    # Fetch paginated orders for the user
    cursor = (
        orders_collection.find({"user_id": user_id}).sort("_id", -1).skip(offset).limit(limit)
    )
    orders_raw = await cursor.to_list(length=limit)
    if not orders_raw:
        return { "data": [], "page": {"next": None, "limit": 0, "previous": None} }

    # Gather all productIds across all orders
    all_product_ids = set(
        str(item["productId"]) for order in orders_raw for item in order["items"]
    )

    # Batch fetch product details
    products = await products_collection.find({"_id": {"$in": [ObjectId(pid) for pid in all_product_ids]}}).to_list(None)
    product_map = {str(prod["_id"]): {"id": str(prod["_id"]), "name": prod["name"]} for prod in products}

    # Build response data
    data = []
    for order_doc in orders_raw:
        items = []
        for item in order_doc["items"]:
            pid = str(item["productId"])
            product_details = {
                "name": product_map.get(pid, {}).get("name", "Unknown Product"),
                "id": pid
            }
            items.append({
                "productDetails": product_details,
                "qty": item["qty"]
            })
        data.append({
            "id": str(order_doc["_id"]),
            "items": items,
            "total": order_doc.get("total_amount", 0.0)
        })

    # Pagination info
    total_count = await orders_collection.count_documents({"user_id": user_id})
    has_next = (offset + limit) < total_count
    has_prev = offset > 0
    page = {
        "next": str(offset + limit) if has_next else None,
        "limit": len(data),
        "previous": offset - limit if has_prev else None
    }
    return {"data": data, "page": page}