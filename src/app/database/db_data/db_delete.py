import asyncio

from app.database.models import Book
from app.database import get_session
from app.database.db_data.seed_data import books_data


async def seed_books(session):
    books = [Book(**book) for book in books_data]
    session.add_all(books)
    await session.commit()

async def main():
    async for session in get_session():
        await seed_books(session)
        print('sxs')

asyncio.run(main())


# async def main():
#     async for session in get_session():
#         # await session.execute(delete(Account))
#         # await session.execute(delete(Admin))
#         # await session.execute(delete(User))
#         # await session.execute(delete(UsersActivity))
#         # await session.execute(delete(user_books_table))
#         # await session.execute(delete(UserActions))
#         # await session.execute(delete(Book).where(Book.title == 'q'))
#         await session.commit()
#         print('sxs')
#
# asyncio.run(main())
