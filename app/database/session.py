from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

engine: AsyncEngine | None = None

_sessionmaker_global: sessionmaker | None = None


# Tries to connect with the DATABASE_URL provided in .env, and use SQLite as a fallback
async def init_engine(database_url: str) -> AsyncEngine:
    global engine, _sessionmaker_global
    try:
        test_engine = create_async_engine(database_url, echo=False)
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        engine = test_engine
    except Exception:
        engine = create_async_engine("sqlite+aiosqlite:///./sqlite.db", echo=False)

    _sessionmaker_global = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    return engine


async def create_db_tables():
    if engine is None:
        raise RuntimeError("Engine not initialized. Call init_engine first.")
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


def get_sessionmaker():
    return _sessionmaker_global


def set_sessionmaker(sm):
    global _sessionmaker_global
    _sessionmaker_global = sm


async def get_session():
    if _sessionmaker_global is None:
        raise RuntimeError("Sessionmaker not initialized. Call init_engine first.")
    async with _sessionmaker_global() as session:
        yield session
        await session.close()
