from typing import Annotated
from fastapi import APIRouter, Depends

from app.api_v1.admin import logic
from app.database import get_session
from app.utils.jwt_funcs import get_current_auth_admin
from app.schemas import (
    AdminSignupSchema,
    AdminSchema,
    BookAddSchema,
    BookEditSchema,
)

router = APIRouter(
    prefix='/admin',
    tags=['Admin'],
)


@router.post('/sign-up')
async def sign_up(
    session: Annotated[get_session, Depends()],
    admin: Annotated[AdminSignupSchema, Depends()]
):
    return await logic.sign_up(session, admin)


@router.get('/get-all-users')
async def get_all_users(
    session: Annotated[get_session, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.get_all_users(session, admin_verifier)


@router.get('/get-user-by-id')
async def get_user_by_id(
    session: Annotated[get_session, Depends()],
    user_id: int,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.get_user_by_id(session, user_id, admin_verifier)


@router.get('/get-all-admins')
async def get_all_admins(
    session: Annotated[get_session, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.get_all_admins(session, admin_verifier)


@router.post('/add-book')
async def add_book(
    session: Annotated[get_session, Depends()],
    data: Annotated[BookAddSchema, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.add_book(session, data, admin_verifier)


@router.post('/delete-book')
async def delete_book(
    session: Annotated[get_session, Depends()],
    book_id: int,
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.delete_book(session, book_id, admin_verifier)


@router.post('/edit-book')
async def edit_book(
    session: Annotated[get_session, Depends()],
    data: Annotated[BookEditSchema, Depends()],
    admin_verifier: AdminSchema = Depends(get_current_auth_admin),
):
    return await logic.edit_book(session, data, admin_verifier)
