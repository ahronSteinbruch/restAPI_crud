# app/models/item.py
from beanie import Document
from pydantic import Field, BaseModel
from typing import Optional

class Item(Document):
    """
    Represents an item document in the MongoDB collection.
    Inherits from Beanie's Document to get full ODM functionality.
    """
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

    class Settings:
        # This defines the name of the collection in MongoDB
        name = "items"

# Pydantic schema for creating an item (input)
# No ID is provided by the client.
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

# Pydantic schema for updating an item (input)
# All fields are optional for partial updates.
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
