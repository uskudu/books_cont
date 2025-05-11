from typing import Annotated
from fastapi import APIRouter, Depends

from app.database import get_session
from app.api_v1.books import logic
from app.schemas import (
    BookFilterSchema,
)

router = APIRouter(
    prefix='/books',
    tags=['Books'],
)


@router.get('/get-all-books')
async def get_all_books(
    session: Annotated[get_session, Depends()]
):
    return await logic.get_all_books(session)


@router.get('/get-book')
async def get_book(
    session: Annotated[get_session, Depends()],
    book_id: int
):
    return await logic.get_book(session, book_id)


@router.get('/search-books')
async def search_books(
    session: Annotated[get_session, Depends()],
    filters: Annotated[BookFilterSchema, Depends()]
):
    return await logic.search_books(session, filters)
