from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = create_async_engine("sqlite+aiosqlite:///./event_feed.db", echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_engine():
    return _engine


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
