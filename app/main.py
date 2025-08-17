# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.api import items

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    The code before 'yield' runs on startup.
    The code after 'yield' runs on shutdown.
    """
    print("Application startup: Initializing database connection...")
    await init_db()
    yield
    print("Application shutdown...")

app = FastAPI(
    title="FastAPI MongoDB CRUD Service",
    version="1.0",
    description="A microservice for managing items, deployed on OpenShift.",
    lifespan=lifespan
)

# Include the API router from the 'items' module.
# All routes defined in 'items.py' will be available under this prefix.
app.include_router(items.router, prefix="/api/v1/items", tags=["Items"])

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the service is running."""
    return {"status": "ok"}
