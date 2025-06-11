from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.admins import services
from app.database import get_session
from app.utils.jwt_funcs import get_current_auth_admin

from fastapi_cache.decorator import cache

from app.schemas.admin import (
    AdminSignupSchema,
    AdminGetSchema,
    AdminSchema,
    AdminGetUserSchema,
    AddBookResponseSchema,
    EditBookResponseSchema,
)
from app.schemas.book import BookAddSchema, BookSchema, BookEditSchema, BookGetSchema

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.post("/sign-up")
async def sign_up(
    session: Annotated[AsyncSession, Depends(get_session)],
    admin: AdminSignupSchema,  # admin: Annotated[AdminSignupSchema, Depends()],
) -> AdminGetSchema:
    return await services.sign_up(session, admin)


@cache(expire=60)
@router.get("/users")
async def get_all_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> list[AdminGetUserSchema]:
    return await services.get_all_users(session, admin_verifier)


@cache(expire=60)
@router.get("/users/{user_id}")
async def get_user_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: str,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> AdminGetUserSchema:
    return await services.get_user_by_id(session, user_id, admin_verifier)


@cache(expire=60)
@router.get("/admins")
async def get_all_admins(
    session: Annotated[AsyncSession, Depends(get_session)],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> list[AdminGetSchema]:
    return await services.get_all_admins(session, admin_verifier)


@router.post("/books", response_model=AddBookResponseSchema)
async def add_book(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: BookAddSchema,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> AddBookResponseSchema:
    return await services.add_book(session, data, admin_verifier)


@router.put("/books/{book_id}", response_model=EditBookResponseSchema)
async def edit_book(
    session: Annotated[AsyncSession, Depends(get_session)],
    book_id: int,
    data: BookEditSchema,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> EditBookResponseSchema:
    return await services.edit_book(session, book_id, data, admin_verifier)


@router.delete("/books/{book_id}")
async def delete_book(
    session: Annotated[AsyncSession, Depends(get_session)],
    book_id: int,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
) -> dict[str, BookGetSchema]:
    return await services.delete_book(session, book_id, admin_verifier)
