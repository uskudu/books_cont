import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.book import BookFilterSchema
from tests.tools import (
    add_books_to_db,
    book_return_value,
)


@pytest.mark.asyncio
async def test_get_all_books(async_session):
    await add_books_to_db(async_session)

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


@pytest.mark.asyncio
async def test_get_all_books_filtered(async_session):
    await add_books_to_db(async_session)

    books_filter_data = BookFilterSchema(
        title="test_title",
        year_max=2030,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        params = books_filter_data.model_dump(exclude_none=True)
        response = await ac.get("/books/", params=params)

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data[0]["title"] == "test_title"
    assert response_data[0]["year"] == 2025
    assert response_data[1]["title"] == "test_title2"
    assert response_data[1]["year"] == 2030
    assert len(response_data) == 2


@pytest.mark.asyncio
async def test_get_book(async_session):
    await add_books_to_db(async_session)
    book_id = 1
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(f"/books/{book_id}")
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data == book_return_value
