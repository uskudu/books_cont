import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import user_books_table
from app.database.models import User, UserActions
from app.schemas.admin import AdminCreateJWTSchema
from app.schemas.jwt import TokenInfoSchema
from app.schemas.user import (
    UserGetSchema,
    UserAddFundsResponseSchema,
    UserCreateJWTSchema,
    DeleteAccountResponse,
    BuyBookResponseSchema,
)
from app.utils import jwt_utils
from app.utils.jwt_funcs import get_admin_from_db_by_username
from app.utils.jwt_utils import (
    create_user_access_token,
    create_admin_access_token,
    hash_password,
)
from app.schemas.user import (
    UserSchema,
    UserSignupSchema,
    UserGetVerifiedSchema,
    UserGetSelfSchema,
    UserDeleteSchema,
    UserAddFundsSchema,
)
from app.schemas.account import AccountSigninSchema
from app.schemas.book import BookSchema, BookGetSchema

from app.api_v1.users.crud import get_user_from_db_by_uid, get_user_from_db_by_username
from app.api_v1.books.crud import get_book_from_db


async def sign_up(
    session: AsyncSession,
    data: UserSignupSchema,
) -> UserGetSchema:
    try:
        user_data_dict = data.model_dump()
        user_data_dict["password"] = hash_password(user_data_dict["password"])
        user_data_dict["user_id"] = str(uuid.uuid4())
        user = User(**user_data_dict)
        session.add(user)

        # update user_actions in db
        new_action = {
            "user_id": user_data_dict["user_id"],
            "action_type": "create_account",
            "details": "created a new account",
            "total": None,
        }
        action = UserActions(**new_action)
        session.add(action)

        await session.commit()
        await session.refresh(user)
        return UserGetSchema.model_validate(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )


async def sign_in(
    session: AsyncSession,
    account: AccountSigninSchema,
) -> TokenInfoSchema:
    user = await get_user_from_db_by_username(session, account.username)

    if user:
        access_token = create_user_access_token(
            UserCreateJWTSchema.model_validate(user)
        )
        new_action = {
            "user_id": user.user_id,
            "action_type": "sign_in",
            "details": "signed in",
            "total": None,
        }
        action = UserActions(**new_action)
        session.add(action)
        await session.commit()
    else:
        admin = await get_admin_from_db_by_username(session, account.username)

        access_token = create_admin_access_token(
            AdminCreateJWTSchema.model_validate(admin)
        )
    return TokenInfoSchema(access_token=access_token)


async def get_my_data(
    session: AsyncSession,
    user_verifier: UserGetVerifiedSchema,
) -> UserGetSelfSchema:
    user = await get_user_from_db_by_uid(session, user_verifier.user_id)
    return UserGetSelfSchema.model_validate(user)


async def add_money(
    session: AsyncSession,
    data: UserAddFundsSchema,
    user_verifier: UserSchema,
) -> UserAddFundsResponseSchema:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    user_from_db.money += data.amount
    balance = user_from_db.money

    # update user_actions in db
    new_action = {
        "user_id": user_verifier.user_id,
        "action_type": "add_money",
        "details": "added money via Superbank FPS",
        "total": data.amount,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    return UserAddFundsResponseSchema(message="Funds added", new_balance=balance)


async def buy_book(
    session: AsyncSession,
    book_id: int,
    user_verifier: UserSchema,
) -> BuyBookResponseSchema:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    book_from_db = await get_book_from_db(session, book_id)

    if not book_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such book doesn't appear to exist",
        )
    if book_from_db.price > user_from_db.money:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have enough money",
        )
    if user_from_db in book_from_db.buyers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You already have this book bought",
        )
    user_from_db.money -= book_from_db.price
    book_from_db.times_bought += 1
    book_from_db.buyers.append(user_from_db)

    # update user_actions in db
    new_action = {
        "user_id": user_verifier.user_id,
        "action_type": "buy_book",
        "details": f"bought a book with id={book_from_db.id}",
        "total": book_from_db.price,
    }
    action = UserActions(**new_action)
    session.add(action)
    await session.commit()
    await session.refresh(book_from_db)

    return BuyBookResponseSchema(
        message="process complete!",
        book=BookGetSchema.model_validate(book_from_db),
    )


async def return_book(
    session: AsyncSession,
    book_id: int,
    user_verifier: UserSchema,
) -> dict[str, str]:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    book_from_db = await get_book_from_db(session, book_id)

    if not book_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such book doesn't appear to exist",
        )
    if user_from_db not in book_from_db.buyers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such book doesn't appear in your books list",
        )

    user_from_db.money += book_from_db.price
    book_from_db.times_returned += 1
    book_from_db.buyers.remove(user_from_db)

    # update user_actions in db
    new_action = {
        "user_id": user_verifier.user_id,
        "action_type": "return_book",
        "details": f"returned a book with id={book_from_db.id}",
        "total": book_from_db.price,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    await session.refresh(book_from_db)

    book_schema = BookSchema.model_validate(book_from_db)
    return {"message": "process complete!", "returned": book_schema.model_dump()}


async def delete_account(
    session: AsyncSession,
    data: UserDeleteSchema,
    user_verifier: UserSchema,
) -> DeleteAccountResponse:
    if not jwt_utils.validate_password(data.password, user_verifier.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    await session.execute(
        delete(user_books_table).where(
            user_books_table.c.user_id == user_verifier.user_id
        )
    )
    await session.execute(
        delete(UserActions)
        .where(UserActions.user_id == user_verifier.user_id)
        .execution_options(is_delete_using=True)
    )
    await session.execute(
        delete(User)
        .where(User.user_id == user_verifier.user_id)
        .execution_options(is_delete_using=True)
    )
    await session.commit()
    return DeleteAccountResponse(success=True, message="account deleted!")
