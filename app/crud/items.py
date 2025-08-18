# app/api/items.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from app.models import Item, ItemCreate, ItemUpdate

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """
    Create a new item.
    - **name**: The item's name (required, 3-50 characters).
    - **description**: An optional description.
    - **price**: The item's price (required, must be > 0).
    """
    new_item = Item(**item.model_dump())
    await new_item.insert()
    return new_item

@router.get("/", response_model=List[Item])
async def get_all_items():
    """
    Retrieve all items from the database.
    """
    items = await Item.find_all().to_list()
    return items

@router.get("/{item_id}", response_model=Item)
async def get_item_by_id(item_id: PydanticObjectId):
    """
    Retrieve a single item by its unique MongoDB ObjectId.
    """
    item = await Item.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")
    return item

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: PydanticObjectId, item_update: ItemUpdate):
    """
    Update an existing item's data.
    You can provide one or more fields to update.
    """
    item = await Item.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")
    
    # Get the update data, excluding fields that were not provided by the client
    update_data = item_update.model_dump(exclude_unset=True)
    
    # Update the item object with the new data and save it
    await item.set(update_data)
    
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: PydanticObjectId):
    """
    Delete an item from the database by its ID.
    """
    item = await Item.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")
    
    await item.delete()
    return None # On successful deletion, return a 204 No Content response
