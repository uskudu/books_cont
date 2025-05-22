from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api_v1.books.crud import get_book_from_db
from app.database.models import Book, User, Admin

from app.schemas import (
    AdminSignupSchema,
    AdminSchema,
    BookAddSchema,
    BookEditSchema,
)

from app.utils.jwt_utils import hash_password, generate_user_id


async def sign_up(
    session: AsyncSession,
    data: AdminSignupSchema,
) -> Admin:
    try:
        admin_data_dict = data.model_dump()
        admin_data_dict["password"] = hash_password(admin_data_dict["password"])
        admin_data_dict["role"] = "admin"
        admin_data_dict["admin_id"] = generate_user_id()
        admin = Admin(**admin_data_dict)
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )


async def get_all_users(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[User]:
    query = await session.execute(
        select(User)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    users = query.scalars().all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )
    return [user.to_dict() for user in users]


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
    admin_verifier: AdminSchema,
) -> User:
    query = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.bought_books))
        .options(selectinload(User.user_actions))
    )
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
    # return UserSchema.model_validate(user)


async def get_all_admins(
    session: AsyncSession,
    admin_verifier: AdminSchema,
) -> list[Admin]:
    query = await session.execute(select(Admin))
    admins = query.scalars().all()
    if not admins:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No admins found"
        )
    return [admin.to_dict() for admin in admins]


async def add_book(
    session: AsyncSession,
    data: BookAddSchema,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
    book_data_dict = data.model_dump()
    book = Book(**book_data_dict)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return {"Successfully added book": book}


async def delete_book(
    session: AsyncSession,
    book_id: int,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
    deleted_book = await get_book_from_db(session, book_id)
    await session.execute(delete(Book).where(Book.id == book_id))
    await session.commit()
    return {"Successfully deleted book": deleted_book}


async def edit_book(
    session: AsyncSession,
    book_id: int,
    data: BookEditSchema,
    admin_verifier: AdminSchema,
) -> dict[str, Book] | None:
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
        return {"Successfully updated book": book_from_db}
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
