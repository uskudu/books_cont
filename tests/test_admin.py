import uuid

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from tests.test_models import Admin

# @pytest.mark.asyncio
# async def test_create_user(async_session):
#     user = User(
#         username="Aliya",
#         password="qwerty",
#         money=123000,
#     )
#     async_session.add(user)
#     await async_session.commit()
#     await async_session.refresh(user)
#
#     assert user.user_id is not None
#     assert user.username == "Aliya"


# @pytest.mark.asyncio
# async def test_add_funds(async_session):
#     stmt = await async_session.execute(select(User).where(User.username == "Aliya"))
#     user = stmt.scalar_one_or_none()
#     assert user.money == 123001
#     user.money += 1
#     await async_session.commit()
#     await async_session.refresh(user)
#     assert user.money == 123002


# # Test: successful admin signup
# @pytest.mark.asyncio
# async def test_sign_up_success(async_session):
#     xxx = str(6)
#     # Arrange
#     signup_data = AdminSignupSchema(
#         username=xxx,
#         password=xxx,
#     )
#
#     # Act
#     result = await sign_up(async_session, signup_data)
#
#     # Assert
#     assert isinstance(result, AdminGetSchema)
#     assert result.username == xxx
#
#     # Verify the admin was saved in the database
#     stmt = select(Admin).where(Admin.username == xxx)
#     saved_admin = (await async_session.execute(stmt)).scalar_one_or_none()
#     assert saved_admin is not None
#     assert saved_admin.username == xxx


@pytest.mark.asyncio
async def test_sign_up(mock_hash_password, async_session):
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
async def test_sign_in(mock_hash_password, async_session):
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


