from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, UserActions
from app.schemas import UserSignupSchema
from app.utils.jwt_utils import hash_password, generate_user_id


async def get_user_from_db_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:
    user = await session.execute(select(User).where(User.username == username))
    return user.scalar_one_or_none()


async def get_user_from_db_by_uid(
    session: AsyncSession,
    uid: str,
) -> User | None:
    user = await session.execute(
        select(User)
        .where(User.user_id == uid)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    return user.scalar_one_or_none()
