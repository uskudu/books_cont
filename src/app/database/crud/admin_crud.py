from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Admin


async def get_admin_from_db_by_uid(
    session: AsyncSession,
    aid: str,
) -> Admin | None:
    admin = await session.execute(select(Admin).where(Admin.admin_id == aid))
    return admin.scalar_one_or_none()


async def get_admin_from_db_by_username(
    session: AsyncSession,
    username: str,
) -> Admin | None:
    admin = await session.execute(select(Admin).where(Admin.username == username))
    return admin.scalar_one_or_none()
