from pydantic import BaseModel, ConfigDict


class BookSchema(BaseModel):
    title: str
    author: str
    genre: str
    description: str = ""
    year: int
    price: int
    times_bought: int = 0
    times_returned: int = 0
    rating: float = 0

    model_config = ConfigDict(from_attributes=True)


class BookAddSchema(BookSchema):
    pass


class BookEditSchema(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    description: str | None = None
    year: int | None = None
    price: int | None = None
    times_bought: int | None = None
    times_returned: int | None = None
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class BookFilterSchema(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    description: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: int | None = None
    price_max: int | None = None
    times_bought_min: int | None = None
    times_bought_max: int | None = None
    times_returned_min: int | None = None
    times_returned_max: int | None = None
    rating_min: float | None = None
    rating_max: float | None = None

    model_config = ConfigDict(from_attributes=True)
