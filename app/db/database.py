# app/db/database.py
from pymongo import MongoClient
from beanie import init_beanie
from app.models import Item
from urllib.parse import quote_plus


def init_db():
    encoded_user = quote_plus(settings.MONGO_USER)
    encoded_password = quote_plus(settings.MONGO_PASSWORD)

    mongo_uri = (
        f"mongodb://{encoded_user}:{encoded_password}@"
        f"{settings.MONGO_HOST}:{settings.MONGO_PORT}/"
        f"{settings.MONGO_DB_NAME}?authSource=admin"
    )
    client = MongoClient(mongo_uri)
    init_beanie(database=client[settings.MONGO_DB_NAME], document_models=[Item])
    print(f"Successfully connected to MongoDB database: {settings.MONGO_DB_NAME}")