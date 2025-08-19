from pydantic import BaseModel, Field
from typing import Optional

# MongoDB משתמש בשדה _id כאובייקט ObjectId.
# אנחנו רוצים שב-API שלנו הוא יוצג כמחרוזת טקסט רגילה.
# נגדיר Type Alias (כינוי) כדי שנוכל להשתמש בו בקלות.
PyObjectId = str

# --- מודלים עבור הדרישה המקורית ---

class OriginalItem(BaseModel):
    """
    מודל זה מייצג את המבנה המדויק של הנתונים כפי שהם נדרשו
    במטלה המקורית, כולל המרת ה-_id של MongoDB.
    """
    # Field(alias='_id') אומר ל-Pydantic:
    # "כשאתה קורא נתונים כדי ליצור את המודל, חפש מפתח בשם '_id'.
    #  כשאתה מייצא את המודל ל-JSON, תשתמש במפתח בשם 'id'."
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    ID: int
    first_name: str
    last_name: str

    class Config:
        # מאפשר ל-Pydantic ליצור את המודל גם אם מקור הנתונים הוא לא dict
        # (למשל, אובייקט של ספרייה אחרת)
        from_attributes = True
        # מאפשר להשתמש ב-alias ('_id') גם בקלט וגם בפלט
        populate_by_name = True

# --- מודלים עבור ה-CRUD המלא (ההרחבה העתידית) ---
# נבנה אותם בצורה מודולרית ונכונה

class ItemBase(BaseModel):
    """
    מודל בסיסי שמכיל את השדות המשותפים שמשתמש יכול לערוך.
    לא כולל את ה-_id או ה-ID המספרי, כי הם מנוהלים על ידי המערכת.
    """
    first_name: str
    last_name: str

class ItemCreate(ItemBase):
    """
    המודל לקבלת נתונים מהמשתמש ליצירת פריט חדש.
    כרגע הוא זהה למודל הבסיס.
    """
    ID: int # נוסיף את ה-ID המספרי שנדרש בטבלה

class ItemUpdate(BaseModel):
    """
    המודל לקבלת נתונים לעדכון. כל השדות אופציונליים,
    כדי שהמשתמש יוכל לעדכן רק שדה אחד אם ירצה.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ItemInDB(ItemBase):
    """
    מודל המייצג פריט שלם כפי שהוא קיים במסד הנתונים,
    כולל השדות שמנוהלים על ידי המערכת.
    """
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    ID: int

    class Config:
        from_attributes = True
        populate_by_name = True