import pytest
import pytest_asyncio
import asyncio
from starlette.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import get_session
from tests.test_models import Base
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///./tests/test.db"


pytestmark = pytest.mark.asyncio


# Fixture: event loop
@pytest.fixture()
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Fixture: async engine
@pytest_asyncio.fixture()
async def async_engine():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# Fixture: async session with database reset
@pytest_asyncio.fixture
async def async_session(async_engine):
    async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        # Reset database state before each test
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        # Override the dependency
        app.dependency_overrides[get_session] = lambda: session
        yield session
        app.dependency_overrides.clear()


@pytest.fixture
def mock_get_session(mocker, async_session):
    # Override the dependency in your FastAPI app
    app.dependency_overrides[get_session] = lambda: async_session
    yield
    # Clear the override after the test
    app.dependency_overrides.clear()


# Fixture: mock hash_password
@pytest.fixture
def mock_hash_password(mocker):
    return mocker.patch(
        "app.api_v1.admins.services.hash_password", return_value="hashed_password"
    )


# Fixture: test client with overridden dependencies
@pytest.fixture
def client(mock_get_session):
    return TestClient(app)
