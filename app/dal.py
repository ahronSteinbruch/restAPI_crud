# app/dal.py
from typing import Any, Dict, List, Optional

from pymongo import AsyncMongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError


class DataLoader:
    """
    קלאס זה הוא המומחה שלנו ל-MongoDB.
    הוא מקבל את פרטי החיבור מבחוץ ואינו תלוי ישירות במשתני סביבה.
    """

    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client: Optional[AsyncMongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None

    async def connect(self):
        """יוצר חיבור א-סינכרוני ל-MongoDB ומאתחל נתונים אם צריך."""
        try:
            self.client = AsyncMongoClient(
                self.mongo_uri, serverSelectionTimeoutMS=5000
            )
            await self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            print("Successfully connected to MongoDB.")
            await self._initialize_data()
        except PyMongoError as e:
            print(f"!!! DATABASE CONNECTION FAILED !!!")
            print(f"Error details: {e}")
            self.client = None
            self.db = None
            self.collection = None

    async def _initialize_data(self):
        """יוצר 5 מסמכים ראשוניים אם האוסף ריק."""
        if self.collection is not None:
            document_count: int = await self.collection.count_documents({})
            if document_count == 0:
                print("Collection is empty. Initializing with sample data...")
                sample_data = [
                    {"ID": 1, "first_name": "John", "last_name": "Doe"},
                    {"ID": 2, "first_name": "Jane", "last_name": "Smith"},
                    {"ID": 3, "first_name": "Peter", "last_name": "Jones"},
                    {"ID": 4, "first_name": "Emily", "last_name": "Williams"},
                    {"ID": 5, "first_name": "Michael", "last_name": "Brown"},
                ]
                await self.collection.insert_many(sample_data)
                print("Sample data inserted.")

    def disconnect(self):
        """סוגר את החיבור למסד הנתונים."""
        if self.client:
            self.client.close()

    async def get_all_data(self):
        """שולף את כל המסמכים מהאוסף 'data'."""
        if self.collection is None:
            return {"error": "Database not connected"}

        items: List[Dict[str, Any]] = []
        async for item in self.collection.find({}):
            item["_id"] = str(item["_id"])
            items.append(item)
        return items
