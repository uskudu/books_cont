from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Account
from app.utils.exceptions import (
    EXC_400_USERNAME_TAKEN,
)
from app.schemas import (
    AdminSignupSchema,
    UserSignupSchema,
)


async def check_username_taken(
    session: AsyncSession,
    data: AdminSignupSchema | UserSignupSchema,
):
    stmt = await session.execute(
        select(Account)
        .where(Account.username == data.username)
    )
    username_taken = stmt.scalar_one_or_none()
    if username_taken:
        raise EXC_400_USERNAME_TAKEN
