import pytest
from tests.test_models import User


@pytest.mark.asyncio
async def test_create_user(async_session):
    user = User(
        username="Aliya",
        password="qwerty",
        money=123000,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    assert user.user_id is not None
    assert user.username == "Aliya"


# @pytest.mark.asyncio
# async def test_create_user(async_session):
