from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

engine: AsyncEngine | None = None

_sessionmaker_global = None


# Tries to connect with the DATABASE_URL provided in .env, and use SQLite as a fallback
async def init_engine(database_url: str) -> AsyncEngine:
    global engine
    try:
        test_engine = create_async_engine(database_url, echo=False)
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        engine = test_engine
    except Exception:
        engine = create_async_engine("sqlite+aiosqlite:///./sqlite.db", echo=False)


async def create_db_tables():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


def get_sessionmaker():
    return _sessionmaker_global


def set_sessionmaker(sm):
    global _sessionmaker_global
    _sessionmaker_global = sm


async def get_session():
    async_session = get_sessionmaker()
    async with async_session() as session:
        yield session


RealSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
set_sessionmaker(RealSessionLocal)
