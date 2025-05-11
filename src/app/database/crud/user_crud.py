from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, UserActions
from app.schemas import UserSignupSchema
from app.utils.jwt_utils import hash_password, generate_user_id


async def add_user_to_db(
    session: AsyncSession,
    data: UserSignupSchema,
):
    user_data_dict = data.model_dump()
    user_data_dict['password'] = hash_password(user_data_dict['password'])
    user_data_dict['role'] = 'user'
    user_data_dict['user_id'] = generate_user_id()
    user = User(**user_data_dict)
    session.add(user)

    # update user_actions in db
    new_action = {
        'user_id': user_data_dict['user_id'],
        'action_type': 'create_account',
        'details': 'created a new account',
        'total': None,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    await session.refresh(user)
    return user


async def get_user_from_db_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:

    user = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    return user.scalar_one_or_none()

async def get_user_from_db_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:
    user = await session.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
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


async def delete_user_from_db(
    session: AsyncSession,
    uid: str,
):
    user = await get_user_from_db_by_uid(session, uid)
    user.active = False
