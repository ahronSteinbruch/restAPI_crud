# app/db/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.item import Item 

async def init_db():
    """
    Initializes the database connection and Beanie ODM.
    """
    # Create a Motor client for connecting to the MongoDB server
    client = AsyncIOMotorClient(settings.MONGO_URI)
    
    # Initialize Beanie with the Item document model.
    # Beanie will use this to map the class to the 'items' collection.
    await init_beanie(database=client[settings.MONGO_DB_NAME], document_models=[Item])
    print(f"Successfully connected to MongoDB database: {settings.MONGO_DB_NAME}")
