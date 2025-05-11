from fastapi import HTTPException
import json

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.common.user_admin import check_username_taken
from app.database.crud.admin_crud import get_all_users_from_db
from app.database.models import Book, User, Admin
from app.core.redis_client import redis_client, serialize_to_json
from app.utils.exceptions import (
    EXC_404_BOOK_NOT_FOUND,
    EXC_404_USER_NOT_FOUND,
)
from app.schemas import (
    AdminSignupSchema,
    AdminSchema,
    BookAddSchema,
    BookEditSchema,
)
from app.database.crud import (
    add_book_to_db,
    get_book_from_db,
    update_book_in_db,
    delete_book_from_db,
    get_user_from_db_by_id,
    add_admin_to_db,
    get_all_admins_from_db,
)


async def sign_up(
    session: AsyncSession,
    data: AdminSignupSchema,
) -> Admin:
    await check_username_taken(session, data)
    return await add_admin_to_db(session, data)


async def get_all_users(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[User]:
    cache_key = 'users:all'
    if cached := redis_client.get(cache_key):
        print('cache hit: get_all_users')
        return json.loads(cached)

    users_dict = await get_all_users_from_db(session)
    serializable_dict = serialize_to_json(users_dict)
    redis_client.set(cache_key, json.dumps(serializable_dict), ex=3600)
    return users_dict


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
    admin_verifier: AdminSchema,
) -> dict:
    cache_key = f'user:{user_id}'
    if cached := redis_client.get(cache_key):
        print('cache hit: get_user_by_id')
        return json.loads(cached)

    user = await get_user_from_db_by_id(session, user_id)
    if user:
        user_dict = await user.to_dict(session)
        serializable_dict = serialize_to_json(user_dict)
        redis_client.set(cache_key, json.dumps(serializable_dict), ex=3600)
        return serializable_dict

    raise EXC_404_USER_NOT_FOUND


async def get_all_admins(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[Admin]:
    cache_key = 'admins:all'
    if cached := redis_client.get(cache_key):
        print('cache hit: get_all_admins')
        return json.loads(cached)

    admins = await get_all_admins_from_db(session)
    redis_client.set(cache_key, json.dumps(admins), ex=3600)
    return admins


async def add_book(
    session: AsyncSession,
    data: BookAddSchema,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
    try:
        book = await add_book_to_db(session, data)
        return {'Successfully added book': book}
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def delete_book(
    session: AsyncSession,
    book_id: int,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
    try:
        book_from_db = await get_book_from_db(session, book_id)
        if book_from_db:
            await delete_book_from_db(session, book_id)
            return {'Successfully deleted book': book_from_db}
    except SQLAlchemyError:
        await session.rollback()
        raise EXC_404_BOOK_NOT_FOUND
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def edit_book(
    session: AsyncSession,
    data: BookEditSchema,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
    try:
        book_from_db = await get_book_from_db(session, data.book_id)
        if not book_from_db:
            raise EXC_404_BOOK_NOT_FOUND

        values_to_update = {}
        for k, v in data.__dict__.items():
            if k == 'book_id' or v is None:
                continue
            match k:
                case 'title':
                    values_to_update['title'] = v
                case 'author':
                    values_to_update['author'] = v
                case 'genre':
                    values_to_update['genre'] = v
                case 'year':
                    values_to_update['year'] = v
                case 'description':
                    values_to_update['description'] = v
                case 'price':
                    values_to_update['price'] = v
                case 'times_bought':
                    values_to_update['times_bought'] = v
                case 'times_returned':
                    values_to_update['times_returned'] = v
                case 'rating':
                    values_to_update['rating'] = v
                case _:
                    pass

        if not values_to_update:
            return {'No updates': book_from_db}

        await update_book_in_db(session, data, values_to_update)

        book_from_db = await get_book_from_db(session, data.book_id)
        return {'Successfully updated book': book_from_db}
    except SQLAlchemyError:
        await session.rollback()
        raise EXC_404_BOOK_NOT_FOUND
