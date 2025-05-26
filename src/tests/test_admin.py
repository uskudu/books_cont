import pytest
from httpx import AsyncClient
from app.main import app
from app.database.models import User
from app.database.db_helper import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.schemas.admin import AdminGetUserSchema


@pytest.mark.asyncio
async def test_get_all_users():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/admins/users")
        print(response)
