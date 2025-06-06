import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Book
from app.api_v1.books.crud import get_book_from_db
from app.schemas.book import (
    BookFilterSchema,
    BookGetSchema,
)


async def get_all_books(
    session: AsyncSession,
    filters: BookFilterSchema,
) -> list[BookGetSchema]:
    query = await session.execute(select(Book))
    books = query.scalars().all()
    # Фильтрация по строковым полям (title, author, genre, description) с частичным совпадением
    for field, value in [
        ("title", filters.title),
        ("author", filters.author),
        ("genre", filters.genre),
        ("description", filters.description),
    ]:
        if value:
            # Игнорируем регистр и используем частичное совпадение
            pattern = re.compile(re.escape(value.lower()), re.IGNORECASE)
            books = [
                book for book in books if pattern.search(getattr(book, field).lower())
            ]

    # Фильтрация по числовым полям (year, price, times_bought, times_returned, rating)
    for field, min_val, max_val in [
        ("year", filters.year_min, filters.year_max),
        ("price", filters.price_min, filters.price_max),
        ("times_bought", filters.times_bought_min, filters.times_bought_max),
        ("times_returned", filters.times_returned_min, filters.times_returned_max),
        ("rating", filters.rating_min, filters.rating_max),
    ]:
        if min_val is not None:
            books = [book for book in books if getattr(book, field) >= min_val]
        if max_val is not None:
            books = [book for book in books if getattr(book, field) <= max_val]
    return [BookGetSchema.model_validate(book) for book in books]


async def get_book(
    session: AsyncSession,
    book_id: int,
) -> BookGetSchema:
    book_from_db = await get_book_from_db(session, book_id)
    return BookGetSchema.model_validate(book_from_db)


class A:
    x = 1


def q():
    return "qwe"


def add(x, y):
    return x + y
