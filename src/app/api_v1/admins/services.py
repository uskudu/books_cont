from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api_v1.books.crud import get_book_from_db
from app.database import user_books_table
from app.database.models import Book, User, Admin
from app.schemas.admin import (
    AdminSignupSchema,
    AdminGetSchema,
    AdminSchema,
    AdminGetUserSchema,
)
from app.schemas.book import BookAddSchema, BookSchema, BookEditSchema

from app.utils.jwt_utils import hash_password


async def sign_up(
    session: AsyncSession,
    data: AdminSignupSchema,
) -> AdminGetSchema:
    try:
        admin_data_dict = data.model_dump()
        admin_data_dict["password"] = hash_password(admin_data_dict["password"])
        admin = Admin(**admin_data_dict)
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return AdminGetSchema.model_validate(admin)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )


async def get_all_users(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[AdminGetUserSchema]:
    query = await session.execute(
        select(User)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    users = query.scalars().all()
    return [AdminGetUserSchema.model_validate(user) for user in users]


async def get_user_by_id(
    session: AsyncSession,
    user_id: str,
    admin_verifier: AdminSchema,
) -> AdminGetUserSchema:
    query = await session.execute(
        select(User)
        .where(User.user_id == user_id)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return AdminGetUserSchema.model_validate(user)


async def get_all_admins(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[AdminGetSchema]:
    query = await session.execute(select(Admin))
    admins = query.scalars().all()
    if not admins:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No admins found"
        )
    return [AdminGetSchema.model_validate(admin) for admin in admins]


async def add_book(
    session: AsyncSession,
    data: BookAddSchema,
    admin_verifier: AdminSchema,
) -> dict[str, BookSchema]:
    book_data_dict = data.model_dump()
    book = Book(**book_data_dict)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return {"Successfully added book": BookSchema.model_validate(book)}


async def edit_book(
    session: AsyncSession,
    book_id: int,
    data: BookEditSchema,
    admin_verifier: AdminSchema,
) -> dict[str, BookSchema]:
    try:
        book_from_db = await get_book_from_db(session, book_id)
        if not book_from_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Such book doesn't appear to exist",
            )
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(book_from_db, key, value)
        await session.commit()
        await session.refresh(book_from_db)
        return {"Successfully updated book": BookSchema.model_validate(book_from_db)}
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_book(
    session: AsyncSession,
    book_id: int,
    admin_verifier: AdminSchema,
) -> dict[str, BookSchema]:
    deleted_book = await get_book_from_db(session, book_id)
    await session.execute(delete(Book).where(Book.id == book_id))
    await session.execute(delete(user_books_table).where(Book.id == book_id))
    await session.commit()
    return {"Successfully deleted book": BookSchema.model_validate(deleted_book)}
