# app/main.py
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI
from .dependencies import data_loader
from . import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # בעליית השרת:
    print("Application startup: connecting to database...")
    await data_loader.connect()
    yield
    # בכיבוי השרת:
    print("Application shutdown: disconnecting from database...")
    data_loader.disconnect()


# יצירת אפליקציית FastAPI
app = FastAPI(
    lifespan=lifespan,
    title="FastAPI MongoDB CRUD Service",
    version="1.0",
    description="A microservice for managing items, deployed on OpenShift.",
)


@app.get(
    "/data",
    response_model=List[models.OriginalItem],
    summary="Get all data (Original Endpoint)",
    tags=["Original Requirement"]
)
async def get_data_endpoint():
    """זוהי נקודת הקצה שנדרשה במבחן."""
    return await data_loader.get_all_data()


@app.get("/")
def health_check_endpoint():
    """נקודת קצה לבדיקת תקינות."""
    return {"status": "ok"}
