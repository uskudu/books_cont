import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.schemas.admin import AdminCreateJWTSchema
from app.schemas.book import BookSchema, BookEditSchema
from app.utils.jwt_utils import create_admin_access_token
from tests.tools import (
    add_book_to_db,
    book_return_value,
)


@pytest.mark.asyncio
async def test_get_all_books(async_session):
    await add_book_to_db(async_session)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/books/")

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data[0]["title"] == "test_title"
    assert response_data[0]["author"] == "test_author"
    assert response_data[0]["genre"] == "test_genre"
    assert response_data[0]["year"] == 2025
    assert response_data[0]["price"] == 100
    assert response_data[0]["times_bought"] == 50
    assert response_data[0]["times_returned"] == 5
