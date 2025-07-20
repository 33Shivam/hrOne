from fastapi import Query
from pydantic import BaseModel

class PageParams(BaseModel):
    limit: int = Query(10, ge=1, le=100)
    offset: int = Query(0, ge=0)

def apply_pagination(cursor, limit: int, offset: int):
    return cursor.skip(offset).limit(limit)
