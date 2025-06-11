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
from tests.test_models import Admin


@pytest.mark.asyncio
async def test_sign_up(async_session, mock_hash_password):
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
        response = await ac.post("/admin/sign-up", json=signup_data)

    # Assert
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["username"] == "test_username"
    assert "admin_id" in response_data
    assert response_data["role"] == "admins"

    result = await async_session.execute(
        select(Admin).where(Admin.username == "test_username")
    )
    saved_admin = result.scalar_one_or_none()

    assert saved_admin is not None
    assert saved_admin.username == "test_username"
    assert saved_admin.password == "hashed_password"
    mock_hash_password.assert_called_once_with("test_password")


@pytest.mark.asyncio
async def test_sign_in(async_session):
    await add_admin_to_db(async_session)

    signin_data = {
        "username": "test_username",
        "password": "test_password",
        "role": "admin",
    }
    # Act
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            url="/user/sign-in",
            data=signin_data,
        )

    # Test
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_get_all_users(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    await add_users_to_db(async_session)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(url="/admin/users", headers=headers)

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data[0]["user_id"] == "test_uid"
    assert response_data[0]["username"] == "test_user1"
    assert response_data[0]["money"] == 777
    assert "user_id" in response_data[1]
    assert response_data[1]["username"] == "test_user2"
    assert response_data[1]["money"] == 0


@pytest.mark.asyncio
async def test_get_user_by_id(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    await add_users_to_db(async_session)
    uid = "test_uid"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            url=f"/admin/users/{uid}",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["user_id"] == "test_uid"
    assert response_data["username"] == "test_user1"
    assert response_data["role"] == "user"
    assert response_data["money"] == 777


@pytest.mark.asyncio
async def test_get_all_admins(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            url="/admin/admins",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    resp = response_data[0]
    assert resp["admin_id"] == "test_aid"
    assert resp["username"] == "test_username"
    assert resp["role"] == "admin"


@pytest.mark.asyncio
async def test_add_book(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    book = BookSchema(
        title="test_title",
        author="test_author",
        genre="test_genre",
        description="test_description",
        year=2025,
        price=100,
        times_bought=50,
        times_returned=5,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            url="/admin/books",
            json=book.model_dump(),
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["message"] == "Successfully added book"
    assert response_data["book"] == book_return_value


@pytest.mark.asyncio
async def test_edit_book(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    await add_books_to_db(async_session)
    book_id = 1
    book_edit_schema = BookEditSchema(
        title="edit_test_title",
        author="edit_test_author",
        genre="edit_test_genre",
        description="edit_test_description",
        year=99,
        price=99,
        times_bought=99,
        times_returned=99,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.put(
            url=f"/admin/books/{book_id}",
            json=book_edit_schema.model_dump(),
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["message"] == "Successfully updated book"
    assert response_data["book"] == {
        "id": 1,
        "title": "edit_test_title",
        "author": "edit_test_author",
        "genre": "edit_test_genre",
        "description": "edit_test_description",
        "year": 99,
        "price": 99,
        "times_bought": 99,
        "times_returned": 99,
        "rating": 0,
    }


@pytest.mark.asyncio
async def test_delete_book(async_session):
    adm = await add_admin_to_db(async_session)
    test_admin = AdminCreateJWTSchema.model_validate(adm)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}

    await add_books_to_db(async_session)
    book_id = 1
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.delete(
            url=f"/admin/books/{book_id}",
            headers=headers,
        )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["message"] == "Successfully deleted book"
    assert response_data["book"] == book_return_value
