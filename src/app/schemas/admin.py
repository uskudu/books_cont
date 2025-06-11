from pydantic import BaseModel, ConfigDict

from app.schemas.book import BookSchema, BookGetSchema
from app.schemas.account import AccountSchema
from app.schemas.user import UserActionsGetSchema, BookOwnedSchema


class AdminSchema(AccountSchema):
    pass


class AdminSignupSchema(AdminSchema):
    pass


class AdminGetSchema(BaseModel):
    admin_id: str
    username: str
    role: str = "admin"

    model_config = ConfigDict(from_attributes=True)


class AdminCreateJWTSchema(BaseModel):
    admin_id: str
    username: str
    role: str = "admin"

    model_config = ConfigDict(from_attributes=True)


class AdminGetUserSchema(BaseModel):
    user_id: str
    username: str
    role: str
    money: int
    bought_books: list[BookOwnedSchema] = []
    user_actions: list[UserActionsGetSchema] = []

    model_config = ConfigDict(from_attributes=True)


class AdminEditedBookResponseSchema(BaseModel):
    message: str
    book: BookSchema


class AdminDeletedBookResponseSchema(BaseModel):
    message: str
    book: BookSchema


class AddBookResponseSchema(BaseModel):
    message: str
    book: BookGetSchema


class EditBookResponseSchema(BaseModel):
    message: str
    book: BookGetSchema


class DeleteBookResponseSchema(BaseModel):
    message: str
    book: BookGetSchema
