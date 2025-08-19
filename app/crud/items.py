from typing import List

from fastapi import APIRouter, HTTPException, status

# מייבאים את המודלים ואת ה-DAL המשותף
from .. import models
from ..dependencies import data_loader

# יוצרים אובייקט APIRouter. חשוב עליו כעל "מיני-אפליקציה" נפרדת.
router = APIRouter(
    prefix="/items",  # כל הנתיבים כאן יתחילו אוטומטית ב-/items
    tags=["Items CRUD"],  # שם הקבוצה בתיעוד ה-Swagger
)


# --- CREATE ---
@router.post("/", response_model=models.ItemInDB, status_code=status.HTTP_201_CREATED)
async def create_item(item: models.ItemCreate):
    """
    יוצר פריט חדש במסד הנתונים.
    """
    try:
        created_item = await data_loader.create_item(item)
        return created_item
    except ValueError as e:
        # תופסים את שגיאת ה-ID הכפול מה-DAL
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


# --- READ (All) ---
@router.get("/", response_model=List[models.ItemInDB])
async def read_all_items():
    """
    שולף את כל הפריטים ממסד הנתונים.
    זוהי הגרסה המודרנית של נקודת הקצה /data.
    """
    try:
        return await data_loader.get_all_data()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


# --- READ (Single) ---
@router.get("/{item_id}", response_model=models.ItemInDB)
async def read_item_by_id(item_id: int):
    """
    שולף פריט בודד לפי ה-ID המספרי שלו.
    """
    try:
        item = await data_loader.get_item_by_id(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found",
            )
        return item
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


# --- UPDATE ---
@router.put("/{item_id}", response_model=models.ItemInDB)
async def update_item(item_id: int, item_update: models.ItemUpdate):
    """
    מעדכן פריט קיים לפי ה-ID המספרי שלו.
    """
    try:
        updated_item = await data_loader.update_item(item_id, item_update)
        if updated_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found to update",
            )
        return updated_item
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


# --- DELETE ---
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """
    מוחק פריט קיים לפי ה-ID המספרי שלו.
    """
    try:
        success = await data_loader.delete_item(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found to delete",
            )
        # עם סטטוס 204, לא מחזירים גוף תשובה
        return
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
