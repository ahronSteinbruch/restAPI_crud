# app/db/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.item import Item
from urllib.parse import quote_plus


async def init_db():
    """
    Initializes the database connection and Beanie ODM.
    """
    # Build the MongoDB URI manually from the settings object
    encoded_user = quote_plus(settings.MONGO_USER)
    encoded_password = quote_plus(settings.MONGO_PASSWORD)

    mongo_uri = (
        f"mongodb://{encoded_user}:{encoded_password}@"
        f"{settings.MONGO_HOST}:{settings.MONGO_PORT}/"
        f"{settings.MONGO_DB_NAME}?authSource=admin"
    )

    # Create a Motor client for connecting to the MongoDB server
    client = AsyncIOMotorClient(mongo_uri)

    # Initialize Beanie with the Item document model.
    # Beanie will use this to map the class to the 'items' collection.
    await init_beanie(database=client[settings.MONGO_DB_NAME], document_models=[Item])
    print(f"Successfully connected to MongoDB database: {settings.MONGO_DB_NAME}")