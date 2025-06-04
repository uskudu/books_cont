from typing import Annotated
from fastapi import APIRouter, Depends, Body, Form
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.users import services
from app.database import get_session
from app.schemas.jwt import TokenInfoSchema
from app.schemas.user import UserAddFundsResponseSchema, UserGetSchema
from app.utils.jwt_funcs import validate_auth_user, get_current_auth_user
from app.schemas.user import (
    UserSchema,
    UserSignupSchema,
    UserGetVerifiedSchema,
    UserGetSelfSchema,
    UserDeleteSchema,
    UserAddFundsSchema,
)
from app.schemas.account import AccountSigninSchema


router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.post("/sign-up")
async def sign_up(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: Annotated[UserSignupSchema, Depends()],
) -> UserGetSchema:
    return await services.sign_up(session, data)


@router.post("/sign-in")
async def sign_in(
    session: Annotated[AsyncSession, Depends(get_session)],
    # account: Annotated[AccountSigninSchema, Depends()],
    username: str = Form(),
    password: str = Form(),
) -> TokenInfoSchema:
    account = AccountSigninSchema(username=username, password=password)
    return await services.sign_in(session, account)


@cache(expire=60)
@router.get("/me", response_model=UserGetSelfSchema)
async def get_my_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_verifier: UserGetVerifiedSchema = Depends(get_current_auth_user),
) -> UserGetSelfSchema:
    return await services.get_my_data(session, user_verifier)


@router.post("/me/add-funds", response_model=UserAddFundsResponseSchema)
async def add_money(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: Annotated[UserAddFundsSchema, Depends()],
    user_verifier: UserSchema = Depends(get_current_auth_user),
) -> UserAddFundsResponseSchema:
    return await services.add_money(session, data, user_verifier)


@router.post("/me/purchase-book")
async def buy_book(
    book_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_verifier: UserSchema = Depends(get_current_auth_user),
) -> dict[str, str]:
    return await services.buy_book(session, book_id, user_verifier)


@router.post("/me/return-book")
async def return_book(
    session: Annotated[AsyncSession, Depends(get_session)],
    book_id: int,
    user_verifier: UserSchema = Depends(get_current_auth_user),
) -> dict[str, str]:
    return await services.return_book(session, book_id, user_verifier)


@router.delete("/me")
async def delete_account(
    data: Annotated[UserDeleteSchema, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_verifier: UserSchema = Depends(get_current_auth_user),
) -> dict[str, str]:
    return await services.delete_account(session, data, user_verifier)
