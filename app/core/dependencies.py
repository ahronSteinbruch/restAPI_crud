import os
from ..dal import DataLoader

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", 27017)
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "test")

mongo_uri = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@"
    f"{MONGO_HOST}:{MONGO_PORT}/"
    f"{MONGO_DB_NAME}?authSource=admin"
)

data_loader = DataLoader(mongo_uri)