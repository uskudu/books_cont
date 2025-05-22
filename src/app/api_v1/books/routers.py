from typing import Annotated
from fastapi import APIRouter, Depends

from app.database import get_session
from app.api_v1.books import services
from app.schemas import (
    BookFilterSchema,
)
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@cache(expire=60)
@router.get("/")
async def get_all_books(
    session: Annotated[get_session, Depends()],
    filters: Annotated[BookFilterSchema, Depends()],
):
    return await services.get_all_books(session, filters)


@router.get("/{book_id}")
async def get_book(session: Annotated[get_session, Depends()], book_id: int):
    return await services.get_book(session, book_id)
