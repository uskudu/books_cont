from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Admin, User
from app.schemas import AdminSignupSchema
from app.schemas.admin_schemas import AdminGetUsersListSchema
from app.utils.jwt_utils import hash_password, generate_user_id


async def add_admin_to_db(
    session: AsyncSession,
    data: AdminSignupSchema,
):
    admin_data_dict = data.model_dump()
    admin_data_dict['password'] = hash_password(admin_data_dict['password'])
    admin_data_dict['role'] = 'admin'
    admin_data_dict['admin_id'] = generate_user_id()
    admin = Admin(**admin_data_dict)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


async def get_all_admins_from_db(
    session: AsyncSession,
) -> list[Admin]:
    query = await session.execute(select(Admin))
    admins = query.scalars().all()
    return [admin.to_dict() for admin in admins]


async def get_all_users_from_db(
    session: AsyncSession,
) -> list[User]:
    query = await session.execute(
        select(User)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    users = query.scalars().all()
    users_t = [await user.to_dict(session) for user in users]
    users_schema = AdminGetUsersListSchema(users=users_t)
    users_dict = users_schema.model_dump()
    return users_dict


async def get_admin_from_db_by_uid(
    session: AsyncSession,
    aid: str,
) -> Admin | None:
    admin = await session.execute(
        select(Admin).where(Admin.admin_id == aid)
    )
    return admin.scalar_one_or_none()


async def get_admin_from_db_by_username(
    session: AsyncSession,
    username: str,
) -> Admin | None:
    admin = await session.execute(
        select(Admin).where(Admin.username == username)
    )
    return admin.scalar_one_or_none()
