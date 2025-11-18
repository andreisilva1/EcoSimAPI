from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from .config import database_settings

database_url = database_settings.DATABASE_URL

try:
    engine = create_async_engine(database_url)
except Exception:
    engine = create_async_engine("sqlite+aiosqlite:///./sqlite.db")


async def create_db_tables():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session
