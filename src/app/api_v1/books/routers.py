from typing import Annotated
from fastapi import APIRouter, Depends

from app.database import get_session
from app.api_v1.books import services
from app.schemas.book_schemas import (
    BookFilterSchema,
    BookGetSchema,
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
) -> list[BookGetSchema]:
    return await services.get_all_books(session, filters)


@cache(expire=60)
@router.get("/{book_id}")
async def get_book(
    session: Annotated[get_session, Depends()], book_id: int
) -> BookGetSchema:
    return await services.get_book(session, book_id)
