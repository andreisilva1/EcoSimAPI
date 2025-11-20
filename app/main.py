import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routers import defaults, plant

from .api.routers import ecosystem, organism
from .database.session import create_db_tables, init_engine

load_dotenv()

database_url = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await init_engine(database_url)
    await create_db_tables()
    yield


app = FastAPI(
    lifespan=lifespan_handler,
    docs_url="/",
    redoc_url=None,
    title="EcoSimAPI",
    version="1.0.0",
)

app.include_router(defaults.router)
app.include_router(ecosystem.router)
app.include_router(organism.router)
app.include_router(plant.router)
