import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.schemas.admin import AdminCreateJWTSchema
from app.schemas.book import BookSchema, BookEditSchema
from app.utils.jwt_utils import create_admin_access_token
from tests.tools import (
    add_books_to_db,
    add_admin_to_db,
    add_users_to_db,
    book_return_value,
)
from tests.test_models import User


@pytest.mark.asyncio
async def test_sign_up(async_session):
    # Arrange
    signup_data = {
        "username": "test_username",
        "password": "test_password",
    }

    # Act
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post("/user/sign-up", json=signup_data)

    # Assert
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert "user_id" in response_data
    assert response_data["username"] == "test_username"
    assert response_data["money"] == 0

    result = await async_session.execute(
        select(User).where(User.username == "test_username")
    )
    saved_user = result.scalar_one_or_none()

    assert saved_user is not None
    assert saved_user.username == "test_username"
    assert saved_user.money is not None
