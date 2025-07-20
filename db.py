from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.mongodb_uri)         # Non-blocking driver[23]
db = client.get_default_database()                        # "ecommerce"
products_collection = db["products"]
orders_collection   = db["orders"]
