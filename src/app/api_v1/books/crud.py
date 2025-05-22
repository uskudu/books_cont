from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Book


async def get_book_from_db(
    session: AsyncSession,
    book_id: int,
) -> Book | None:
    query = await session.execute(
        select(Book).where(Book.id == book_id).options(selectinload(Book.buyers))
    )
    book = query.scalar_one_or_none()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book
