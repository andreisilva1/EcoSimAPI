from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import plant

from .api.routers import ecosystem, organism
from .database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    lifespan=lifespan_handler,
    docs_url="/",
    redoc_url=None,
    title="EcoSimAPI",
    version="1.0.0",
)
app.include_router(ecosystem.router)
app.include_router(organism.router)
app.include_router(plant.router)
