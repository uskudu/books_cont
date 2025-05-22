from fastapi import Form, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.database.models import User, Admin
from app.utils import jwt_utils
from app.api_v1.admin.crud import (
    get_admin_from_db_by_username,
    get_admin_from_db_by_uid,
)
from app.api_v1.users.crud import (
    get_user_from_db_by_uid,
    get_user_from_db_by_username,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/sign-in")


async def validate_auth_user(
    session: AsyncSession = Depends(get_session),
    username: str = Form(),
    password: str = Form(),
) -> Admin | User:
    user_from_db = await get_user_from_db_by_username(session, username)
    admin_from_db = await get_admin_from_db_by_username(session, username)

    if user_from_db and user_from_db.active:
        if jwt_utils.validate_password(password, user_from_db.password):
            return user_from_db
    if admin_from_db:
        if jwt_utils.validate_password(password, admin_from_db.password):
            return admin_from_db
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
    )


def get_current_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        return jwt_utils.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid token error: {e}"
        )


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id_from_token: str = payload.get("sub")

    user_from_db = await get_user_from_db_by_uid(session, user_id_from_token)
    if not user_from_db or not user_from_db.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token: you do not have access to this function",
        )
    return user_from_db


async def get_current_auth_admin(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_session),
) -> Admin:
    admin_id_from_token: str = payload.get("sub")

    admin_from_db = await get_admin_from_db_by_uid(session, admin_id_from_token)
    if admin_from_db:
        return admin_from_db
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid token: you do not have access to this function",
    )
