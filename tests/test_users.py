import bcrypt
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.main import app
from app.schemas.user import UserCreateJWTSchema, UserAddFundsSchema, UserDeleteSchema
from app.utils.jwt_utils import create_user_access_token
from tests.tools import (
    add_books_to_db,
    add_user_to_db,
)
from tests.test_models import User, Book


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


@pytest.mark.asyncio
async def test_buy_book(async_session):
    await add_books_to_db(async_session)
    headers = await user_auth(async_session)
    book_id = 1

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            url=f"/user/me/purchase-book/{book_id}",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()

    title = "test_title"
    author = "test_author"
    year = 2025

    assert response_data["message"] == "process complete!"
    assert response_data["bought"]["title"] == title
    assert response_data["bought"]["author"] == author
    assert response_data["bought"]["year"] == year

    result = await async_session.execute(select(Book).where(Book.id == book_id))
    saved_book = result.scalar_one_or_none()
    assert saved_book.title == title
    assert saved_book.author == author
    assert saved_book.year == 2025

    result = await async_session.execute(
        select(User)
        .where(User.user_id == "test_uid")
        .options(selectinload(User.bought_books))
    )
    saved_user = result.scalar_one_or_none()
    assert len(saved_user.bought_books) == 1


@pytest.mark.asyncio
async def test_return_book(async_session):
    await add_books_to_db(async_session)
    headers = await user_auth(async_session)
    book_id = 1

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        await ac.post(
            url=f"/user/me/purchase-book/{book_id}",
            headers=headers,
        ),
        response = await ac.post(
            url=f"/user/me/return-book/{book_id}",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()

    title = "test_title"
    author = "test_author"
    year = 2025

    assert response_data["message"] == "process complete!"
    assert response_data["returned"]["title"] == title
    assert response_data["returned"]["author"] == author
    assert response_data["returned"]["year"] == year

    result = await async_session.execute(select(Book).where(Book.id == book_id))
    saved_book = result.scalar_one_or_none()
    assert saved_book.title == title
    assert saved_book.author == author
    assert saved_book.year == 2025


@pytest.mark.asyncio
async def test_delete_account(async_session):
    headers = await user_auth(async_session)
    pswd = UserDeleteSchema(password="test_password")

    result = await async_session.execute(select(User).where(User.user_id == "test_uid"))
    saved_user = result.scalar_one_or_none()
    assert saved_user is not None

    hashed_password = bcrypt.hashpw("test_password".encode(), bcrypt.gensalt()).decode()
    saved_user.password = hashed_password
    await async_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.request(
            method="DELETE",
            url=f"/user/me",
            headers=headers,
            json=pswd.model_dump(),
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["success"] == True
    assert response_data["message"] == "account deleted!"

    result = await async_session.execute(select(User).where(User.user_id == "test_uid"))
    saved_user = result.scalar_one_or_none()
    assert saved_user is None
