from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Book
from app.schemas import BookEditSchema, BookAddSchema


async def add_book_to_db(
    session: AsyncSession,
    data: BookAddSchema,
) -> Book:
    book_data_dict = data.model_dump()
    book = Book(**book_data_dict)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def get_book_from_db(
    session: AsyncSession,
    book_id: int,
) -> Book | None:
    book = await session.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(selectinload(Book.buyers))
    )
    return book.scalar_one_or_none()


async def get_all_books_from_db(
    session: AsyncSession
) -> list[Book] | None:
    query = await session.execute(select(Book))
    books = query.scalars().all()
    return [book.to_dict() for book in books]


async def update_book_in_db(
    session: AsyncSession,
    data: BookEditSchema,
    values_to_update: dict,
) -> None:
    result = await session.execute(select(Book).where(Book.id == data.book_id))
    book = result.scalar_one_or_none()
    for key, value in values_to_update.items():
        setattr(book, key, value)
    await session.commit()


async def delete_book_from_db(
    session: AsyncSession,
    book_id: int
) -> None:
    await session.execute(
        delete(Book)
        .where(Book.id == book_id)
    )
    await session.commit()
