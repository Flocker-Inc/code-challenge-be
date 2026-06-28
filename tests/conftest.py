import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src import session as session_module
from src.app import app as _app
from src.core.base_model import Base

API_KEY = "flocker-challenge-key-2024"

_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
test_engine = create_async_engine(f"sqlite+aiosqlite:///{_test_db_path}", echo=False)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    session_module._engine = test_engine
    session_module._session_factory = test_session_factory
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    test_engine.sync_engine.dispose()
    os.close(_test_db_fd)
    os.unlink(_test_db_path)


@pytest.fixture
async def session():
    async with test_engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn) as session:
            yield session
        await conn.rollback()


@pytest.fixture
def app():
    return _app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY}
