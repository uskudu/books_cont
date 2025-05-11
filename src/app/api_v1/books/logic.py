import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_client, serialize_to_json
from app.database.models import Book
from app.utils.exceptions import EXC_404_BOOK_NOT_FOUND
from app.database.crud import (
    get_book_from_db,
    get_all_books_from_db,
)
from app.schemas import (
    BookSchema,
    BookFilterSchema,
)


async def get_all_books(session: AsyncSession) -> list[Book]:
    cache_key = 'books:all'
    if cached := redis_client.get(cache_key):
        print('cache hit: get_all_books')
        return json.loads(cached)

    books = await get_all_books_from_db(session)
    redis_client.set(cache_key, json.dumps(books), ex=3600)
    return books


async def get_book(
    session: AsyncSession,
    book_id: int,
) -> Book:
    cache_key = f'book:{book_id}'
    if cached := redis_client.get(cache_key):
        print('cache hit: get_book_by_id')
        return json.loads(cached)

    book = await get_book_from_db(session, book_id)
    if book:
        book_dict = book.to_dict()
        serializable_dict = serialize_to_json(book_dict)
        redis_client.set(cache_key, json.dumps(serializable_dict), ex=3600)
        return serializable_dict
    raise EXC_404_BOOK_NOT_FOUND


async def search_books(
    session: AsyncSession,
    filters: BookFilterSchema
) -> list[BookSchema]:
    books = await get_all_books_from_db(session)

    # Фильтрация по строковым полям (title, author, genre, description) с частичным совпадением
    for field, value in [
        ('title', filters.title),
        ('author', filters.author),
        ('genre', filters.genre),
        ('description', filters.description)
    ]:
        if value:
            # Игнорируем регистр и используем частичное совпадение
            pattern = re.compile(re.escape(value.lower()), re.IGNORECASE)
            books = [
                book for book in books
                if pattern.search(getattr(book, field).lower())
            ]

    # Фильтрация по числовым полям (year, price, times_bought, times_returned, rating)
    for field, min_val, max_val in [
        ('year', filters.year_min, filters.year_max),
        ('price', filters.price_min, filters.price_max),
        ('times_bought', filters.times_bought_min, filters.times_bought_max),
        ('times_returned', filters.times_returned_min, filters.times_returned_max),
        ('rating', filters.rating_min, filters.rating_max),
    ]:
        if min_val is not None:
            books = [
                book for book in books
                if getattr(book, field) >= min_val
            ]
        if max_val is not None:
            books = [
                book for book in books
                if getattr(book, field) <= max_val
            ]
    return books
