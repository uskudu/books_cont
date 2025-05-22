from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache

from app.api_v1.admin import services
from app.database import get_session
from app.utils.jwt_funcs import get_current_auth_admin
from app.schemas import (
    AdminSignupSchema,
    AdminSchema,
    BookAddSchema,
    BookEditSchema,
)
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.post("/sign-up")
async def sign_up(
    session: Annotated[get_session, Depends()],
    admin: Annotated[AdminSignupSchema, Depends()],
):
    return await services.sign_up(session, admin)


@router.get("/users")
@cache(expire=60)
async def get_all_users(
    session: Annotated[get_session, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.get_all_users(session, admin_verifier)


@cache(expire=60)
@router.get("/users/{user_id}")
async def get_user_by_id(
    session: Annotated[get_session, Depends()],
    user_id: int,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.get_user_by_id(session, user_id, admin_verifier)


def custom_key_builder(func, namespace, request, response, *args, **kwargs):
    key = FastAPICache.get_prefix() + ":" + namespace
    key += ":" + request.url.path
    print(f"[KEY BUILDER] Cache key built: {key}")
    return key


@cache(expire=60, key_builder=custom_key_builder)
@router.get("/admins")
async def get_all_admins(
    session: Annotated[get_session, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.get_all_admins(session, admin_verifier)


@router.post("/books")
async def add_book(
    session: Annotated[get_session, Depends()],
    data: Annotated[BookAddSchema, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.add_book(session, data, admin_verifier)


@router.delete("/books/{book_id}")
async def delete_book(
    session: Annotated[get_session, Depends()],
    book_id: int,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.delete_book(session, book_id, admin_verifier)


@router.put("/books/{book_id}")
async def edit_book(
    session: Annotated[get_session, Depends()],
    book_id: int,
    data: Annotated[BookEditSchema, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await services.edit_book(session, book_id, data, admin_verifier)
