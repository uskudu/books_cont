from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.common.user_admin import check_username_taken
from app.database.models import User, UserActions
from app.utils import jwt_utils
from app.utils.jwt_utils import (
    create_user_access_token, create_admin_access_token,
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
    add_user_to_db,
    delete_user_from_db,
    get_book_from_db, get_user_from_db_by_username
)
from app.utils.exceptions import (
    EXC_404_BOOK_NOT_FOUND,
    EXC_400_BOOK_ALREADY_BOUGHT,
    EXC_400_BOOK_NOT_BOUGHT,
    EXC_403_NOT_ENOUGH_MONEY,
)


async def sign_up(
    session: AsyncSession,
    data: UserSignupSchema,
) -> User:
    await check_username_taken(session, data)
    return await add_user_to_db(session, data)


async def sign_in(
    session: AsyncSession,
    account: AccountSigninSchema,
):
    user_from_db = await get_user_from_db_by_username(session, account.username)

    if user_from_db:
        access_token = create_user_access_token(account)
        new_action = {
            'user_id': user_from_db.user_id,
            'action_type': 'sign_in',
            'details': 'signed in',
            'total': None,
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
        raise HTTPException(status_code=401, detail='Invalid password')

    # update user_actions in db
    new_action = {
        'user_id': user_verifier.user_id,
        'action_type': 'delete_account',
        'details': 'deleted an account',
        'total': None,
    }
    action = UserActions(**new_action)
    session.add(action)
    await session.flush()
    await delete_user_from_db(session, user_verifier.user_id)
    await session.commit()
    return {'success': True, 'message': 'Account deleted'}


async def get_my_data(
    session: AsyncSession,
    user_verifier: UserGetSchema,
) -> dict:
    user_dict = await user_verifier.to_dict(session=session)
    user_schema = UserGetSelfSchema.model_validate(user_dict)
    return user_schema.model_dump()


async def add_money(
    session: AsyncSession,
    data: UserAddMoneySchema,
    user_verifier: UserSchema,
) -> dict[str, str]:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    user_from_db.money += data.amount

    # update user_actions in db
    new_action = {
        'user_id': user_verifier.user_id,
        'action_type': 'add_money',
        'details': 'added money via Superbank FPS',
        'total': data.amount,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    return {'message': 'Funds added'}


async def buy_book(
    session: AsyncSession,
    book_id: int,
    user_verifier: UserSchema,
) -> dict[str, str]:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    book_from_db = await get_book_from_db(session, book_id)

    if not book_from_db:
        await session.rollback()
        raise EXC_404_BOOK_NOT_FOUND
    if book_from_db.price > user_from_db.money:
        await session.rollback()
        raise EXC_403_NOT_ENOUGH_MONEY
    if user_from_db in book_from_db.buyers:
        await session.rollback()
        raise EXC_400_BOOK_ALREADY_BOUGHT

    user_from_db.money -= book_from_db.price
    book_from_db.times_bought += 1

    book_from_db.buyers.append(user_from_db)

    # update user_actions in db
    new_action = {
        'user_id': user_verifier.user_id,
        'action_type': 'buy_book',
        'details': f'bought a book with id={book_from_db.id}',
        'total': book_from_db.price,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    await session.refresh(book_from_db)

    book_schema = BookSchema.model_validate(book_from_db, from_attributes=True)
    return {'message': 'process complete!', 'bought': f'{book_schema.model_dump()}'}


async def return_book(
    session: AsyncSession,
    book_id: int,
    user_verifier: UserSchema,
) -> dict[str, str]:
    user_from_db = await get_user_from_db_by_uid(session, user_verifier.user_id)
    book_from_db = await get_book_from_db(session, book_id)

    if not book_from_db:
        raise EXC_404_BOOK_NOT_FOUND
    if user_from_db not in book_from_db.buyers:
        raise EXC_400_BOOK_NOT_BOUGHT

    user_from_db.money += book_from_db.price
    book_from_db.times_returned += 1

    book_from_db.buyers.remove(user_from_db)

    # update user_actions in db
    new_action = {
        'user_id': user_verifier.user_id,
        'action_type': 'return_book',
        'details': f'returned a book with id={book_from_db.id}',
        'total': book_from_db.price,
    }
    action = UserActions(**new_action)
    session.add(action)

    await session.commit()
    await session.refresh(book_from_db)

    book_schema = BookSchema.model_validate(book_from_db, from_attributes=True)
    return {'message': 'Process complete', 'Returned': f'{book_schema.model_dump()}'}
