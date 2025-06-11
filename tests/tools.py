import uuid
from tests.test_models import Admin, User, Book


book_return_value = {
    "id": 1,
    "title": "test_title",
    "author": "test_author",
    "genre": "test_genre",
    "description": "test_description",
    "year": 2025,
    "price": 100,
    "times_bought": 50,
    "times_returned": 5,
    "rating": 0.0,
}


async def add_books_to_db(async_session):
    books = [
        Book(
            id=1,
            title="test_title",
            author="test_author",
            genre="test_genre",
            description="test_description",
            year=2025,
            price=100,
            times_bought=50,
            times_returned=5,
        ),
        Book(
            id=2,
            title="test_title2",
            author="test_author2",
            genre="test_genre2",
            description="test_description2",
            year=2030,
            price=150,
            times_bought=55,
            times_returned=10,
        ),
        Book(
            id=3,
            title="test_title3",
            author="test_author3",
            genre="test_genre3",
            description="test_description3",
            year=2035,
            price=200,
            times_bought=60,
            times_returned=15,
        ),
    ]
    async_session.add_all(books)
    await async_session.commit()
    for book in books:
        await async_session.refresh(book)
    return books


async def add_admin_to_db(async_session):
    adm = Admin(
        admin_id="test_aid",
        username="test_username",
        password="test_password",
        role="admin",
    )
    async_session.add(adm)
    await async_session.commit()
    await async_session.refresh(adm)
    return adm


async def add_user_to_db(async_session):
    user = User(
        user_id="test_uid",
        username="test_user1",
        password="test_password",
        role="user",
        money=777,
    )

    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


async def add_users_to_db(async_session):
    users = [
        User(
            user_id="test_uid",
            username="test_user1",
            password="test_password",
            role="user",
            money=777,
        ),
        User(
            user_id=str(uuid.uuid4()),
            username="test_user2",
            password="test_password",
            role="user",
        ),
        User(
            user_id=str(uuid.uuid4()),
            username="test_user3",
            password="test_password",
            role="user",
        ),
    ]

    async_session.add_all(users)
    await async_session.commit()
    for user in users:
        await async_session.refresh(user)
    return users
