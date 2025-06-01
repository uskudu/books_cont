import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from app.main import app
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from tests.test_models import Base

DATABASE_URL = "sqlite+aiosqlite:///./tests/test.db"

pytestmark = pytest.mark.asyncio


# Fixture: event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Fixture: async engine
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# Fixture: async session
@pytest_asyncio.fixture
async def async_session(async_engine):
    async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


# Fixture: test client
@pytest.fixture
def client():
    return TestClient(app)
