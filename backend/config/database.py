"""
Database configuration and connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
from .settings import MONGO_URL, DB_NAME

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collection references for convenience
users_collection = db.users
parlays_collection = db.parlays
predictions_collection = db.predictions
recovery_codes_collection = db.recovery_codes
