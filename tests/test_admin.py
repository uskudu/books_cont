import uuid

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.schemas.admin import AdminSchema, AdminCreateJWTSchema
from app.utils.jwt_utils import create_admin_access_token
from tests.test_models import Admin


@pytest.mark.asyncio
async def test_sign_up(async_session, mock_hash_password):
    # Arrange
    signup_data = {
        "username": "admin1",
        "password": "plain_password",
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
    assert response_data["username"] == "admin1"
    assert "admin_id" in response_data
    assert response_data["role"] == "admins"

    result = await async_session.execute(
        select(Admin).where(Admin.username == "admin1")
    )
    saved_admin = result.scalar_one_or_none()

    assert saved_admin is not None
    assert saved_admin.username == "admin1"
    assert saved_admin.password == "hashed_password"
    mock_hash_password.assert_called_once_with("plain_password")


@pytest.mark.asyncio
async def test_sign_in(async_session, mock_hash_password):
    adm = Admin(
        admin_id=str(uuid.uuid4()),
        username="admin1",
        password="plain_password",
        role="admin",
    )
    async_session.add(adm)
    await async_session.commit()

    signin_data = {
        "username": "admin1",
        "password": "plain_password",
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
async def test_get_all_users(async_session, mock_hash_password):
    adm = Admin(
        admin_id=str(uuid.uuid4()),
        username="test_name",
        password="test_password",
        role="admin",
    )
    async_session.add(adm)
    await async_session.commit()

    stmt = await async_session.execute(
        select(Admin).where(Admin.username == "test_name")
    )
    admin_from_db = stmt.scalar_one_or_none()
    test_admin = AdminCreateJWTSchema.model_validate(admin_from_db)
    token = create_admin_access_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}
    # then test
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(url="/admin/users", headers=headers)

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
