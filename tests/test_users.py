from http.client import responses

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.schemas.admin import AdminCreateJWTSchema
from app.schemas.book import BookSchema, BookEditSchema
from app.schemas.user import UserCreateJWTSchema, UserAddFundsSchema
from app.utils.jwt_utils import create_admin_access_token, create_user_access_token
from tests.tools import (
    add_books_to_db,
    add_admin_to_db,
    add_users_to_db,
    book_return_value,
    add_user_to_db,
)
from tests.test_models import User


# tool
async def user_auth(async_session):
    usr = await add_user_to_db(async_session)
    test_user = UserCreateJWTSchema.model_validate(usr)
    token = create_user_access_token(test_user)
    headers = {"Authorization": f"Bearer {token}"}
    return headers


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


@pytest.mark.asyncio
async def test_sign_in(async_session):
    await add_user_to_db(async_session)

    signin_data = {
        "username": "test_user1",
        "password": "test_password",
        "role": "user",
        "money": 777,
    }
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            url="/user/sign-in",
            data=signin_data,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_get_my_data(async_session):
    headers = await user_auth(async_session)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            url="/user/me",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()

    assert response_data["user_id"] == "test_uid"
    assert response_data["username"] == "test_user1"
    assert response_data["money"] == 777
    assert response_data["bought_books"] == []


@pytest.mark.asyncio
async def test_add_money(async_session):
    headers = await user_auth(async_session)
    amount = UserAddFundsSchema(amount=223)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            url="/user/me/add-funds",
            headers=headers,
            json=amount.model_dump(),
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["message"] == "Funds added"
    assert response_data["new_balance"] == 1000

    result = await async_session.execute(
        select(User).where(User.username == "test_user1")
    )
    saved_user = result.scalar_one_or_none()
    assert saved_user.money == 1000
