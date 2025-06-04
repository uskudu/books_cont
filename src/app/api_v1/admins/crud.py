from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import Admin


async def get_admin_from_db_by_username(
    session: AsyncSession,
    username: str,
) -> Admin | None:
    admin = await session.execute(select(Admin).where(Admin.username == username))
    return admin.scalar_one_or_none()
