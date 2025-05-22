from typing import Annotated
from fastapi import APIRouter, Depends

from app.api_v1.users import services
from app.database import get_session
from app.utils.jwt_funcs import validate_auth_user, get_current_auth_user
from app.schemas import (
    AccountSigninSchema,
    UserSchema,
    UserSignupSchema,
    UserGetSchema,
    UserDeleteSchema,
    UserAddMoneySchema,
    UserGetSelfSchema,
)
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.post("/sign-up")
async def sign_up(
    session: Annotated[get_session, Depends()],
    data: Annotated[UserSignupSchema, Depends()],
):
    return await services.sign_up(session, data)


@router.post("/sign-in")
async def sign_in(
    session: Annotated[get_session, Depends()],
    account: AccountSigninSchema = Depends(validate_auth_user),
):
    return await services.sign_in(session, account)


@router.delete("/me")
async def delete_account(
    data: Annotated[UserDeleteSchema, Depends()],
    session: Annotated[get_session, Depends()],
    user_verifier: UserSchema = Depends(get_current_auth_user),
):
    return await services.delete_account(session, data, user_verifier)


# @cache(expire=60)
@router.get("/me", response_model=UserGetSelfSchema)
async def get_my_data(
    session: Annotated[get_session, Depends()],
    user_verifier: UserGetSchema = Depends(get_current_auth_user),
):
    return await services.get_my_data(session, user_verifier)


@router.post("/me/add-funds")
async def add_money(
    session: Annotated[get_session, Depends()],
    data: Annotated[UserAddMoneySchema, Depends()],
    user_verifier: UserSchema = Depends(get_current_auth_user),
):
    return await services.add_money(session, data, user_verifier)


@router.post("/me/purchase-book")
async def buy_book(
    book_id: int,
    session: Annotated[get_session, Depends()],
    user_verifier: UserSchema = Depends(get_current_auth_user),
):
    return await services.buy_book(session, book_id, user_verifier)


@router.post("/me/return-book")
async def return_book(
    session: Annotated[get_session, Depends()],
    book_id: int,
    user_verifier: UserSchema = Depends(get_current_auth_user),
):
    return await services.return_book(session, book_id, user_verifier)
