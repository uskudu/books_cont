from pydantic import BaseModel, ConfigDict

from app.schemas.book_schemas import BookSchema
from app.schemas.account_schemas import AccountSchema
from app.schemas.user_schemas import UserActionsGetSchema, BookOwnedSchema


class AdminSchema(AccountSchema):
    pass


class AdminSignupSchema(AdminSchema):
    pass


class AdminGetSchema(BaseModel):
    admin_id: str
    username: int
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
