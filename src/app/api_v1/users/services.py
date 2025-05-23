from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.models import User, UserActions
from app.utils import jwt_utils
from app.utils.jwt_utils import (
    create_user_access_token,
    create_admin_access_token,
    hash_password,
    generate_user_id,
)
from app.schemas import (
    TokenInfoSchema,
    AccountSigninSchema,
    UserSchema,
    UserSignupSchema,
    UserGetSchema,
    UserGetSelfSchema,
    UserDeleteSchema,
    UserAddMoneySchema,
    BookSchema,
)
from app.database.crud import (
    get_user_from_db_by_uid,
    get_book_from_db,
    get_user_from_db_by_username,
)


async def sign_up(
    session: AsyncSession,
    data: UserSignupSchema,
) -> User:
    try:
        user_data_dict = data.model_dump()
        user_data_dict["password"] = hash_password(user_data_dict["password"])
        user_data_dict["role"] = "user"
        user_data_dict["user_id"] = generate_user_id()
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
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )


async def sign_in(
    session: AsyncSession,
    account: AccountSigninSchema,
):
    user = await get_user_from_db_by_username(session, account.username)

    if user:
        access_token = create_user_access_token(account)
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
        access_token = create_admin_access_token(account)
    return TokenInfoSchema(access_token=access_token)


async def delete_account(
    session: AsyncSession,
    data: UserDeleteSchema,
    user_verifier: UserSchema,
) -> dict[str, str]:
    if not jwt_utils.validate_password(data.password, user_verifier.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    user = await get_user_from_db_by_uid(session, user_verifier.user_id)
    user.active = False  # delete user (deactivate)

    # update user_actions in db
    new_action = {
        "user_id": user_verifier.user_id,
        "action_type": "delete_account",
        "details": "deleted account",
        "total": None,
    }
    action = UserActions(**new_action)
    session.add(action)
    await session.commit()
    return {"success": True, "message": "Account deleted"}


async def get_my_data(
    session: AsyncSession,
    user_verifier: UserGetSchema,
) -> UserGetSelfSchema:
    user_dict = user_verifier.to_dict()
    user_schema = UserGetSelfSchema.model_validate(user_dict)
    return UserGetSelfSchema.model_validate(user_schema)


async def add_money(
    session: AsyncSession,
    data: UserAddMoneySchema,
    user_verifier: UserSchema,
) -> dict[str, str]:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    user_from_db.money += data.amount

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
    return {"message": "Funds added"}


async def buy_book(
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

    book_schema = BookSchema.model_validate(book_from_db, from_attributes=True)
    return {"message": "process complete!", "bought": f"{book_schema.model_dump()}"}


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

    book_schema = BookSchema.model_validate(book_from_db, from_attributes=True)
    return {"message": "Process complete", "Returned": f"{book_schema.model_dump()}"}
