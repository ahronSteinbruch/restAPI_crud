# app/main.py
from fastapi import FastAPI, HTTPException
from .core.dependencies import data_loader
from contextlib import asynccontextmanager
from typing import List
from .crud import items
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    The code before 'yield' runs on startup.
    The code after 'yield' runs on shutdown.
    """
    print("Application startup: Initializing database connection...")
    data_loader.connect()
    yield
    print("Application shutdown...")
    data_loader.disconnect()

app = FastAPI(
    title="FastAPI MongoDB CRUD Service",
    version="1.0",
    description="A microservice for managing items, deployed on OpenShift.",
    lifespan=lifespan
)

# Include the API router from the 'items' module.
# All routes defined in 'items.py' will be available under this prefix.
#app.include_router(items.router, prefix="/api/v1/items", tags=["Items"])

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the service is running."""
    return {"status": "ok"}


@app.get(
    "/data",
    # ★★★ הוספת ה-response_model ★★★
    response_model=List[models.Item],
    summary="Get all data (Legacy)",
    description="The original endpoint to fetch all records from the 'data' table.",
    tags=["Legacy"],
)
def get_all_data_legacy():
    """
    This is the original endpoint required by the project.
    For a more conventional REST API, use GET /items/ instead.
    """
    try:
        all_data = data_loader.get_all_data()
        return all_data
    except Exception as e:
        pass

