# data_loader/dependencies.py
import os

from .dal import DataLoader  # ייבוא הקלאס שיצרנו

# קריאת התצורה ממשתני הסביבה, במקום אחד מרכזי
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mydatabase")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "data")

# אם אין שם משתמש, נבנה URI פשוט יותר.
if MONGO_USER and MONGO_PASSWORD:
    # URI למצב עם אימות (יעבוד ב-OpenShift)
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
else:
    # URI למצב ללא אימות (עבור הדוקר הלוקאלי שלך)
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

# יצירת המופע האחד והיחיד (Singleton) של ה-DAL.
# כל שאר חלקי האפליקציה ייבאו את המשתנה הזה.
data_loader = DataLoader(
    mongo_uri=MONGO_URI, db_name=MONGO_DB_NAME, collection_name=MONGO_COLLECTION_NAME
)
