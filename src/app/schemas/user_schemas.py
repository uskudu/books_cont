from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.account_schemas import AccountSchema


class BookOwnedSchema(BaseModel):
    title: str
    author: str
    genre: str
    year: int
    description: str
    price: int
    times_bought: int
    times_returned: int
    rating: float


class UserSchema(AccountSchema):
    pass


class UserSignupSchema(UserSchema):
    pass


class UserSigninSchema(UserSchema):
    pass


class UserGetSchema(UserSchema):
    pass


class UserActionsGetSchema(BaseModel):
    user_id: str
    action_type: str
    details: str
    total: int | None
    timestamp: datetime


class UserGetSelfSchema(BaseModel):
    username: str
    money: int
    bought_books: list[BookOwnedSchema]
    actions_history: list[UserActionsGetSchema]


class UserDeleteSchema(BaseModel):
    password: str


class UserAddMoneySchema(BaseModel):
    amount: int = Field(lt=2_147_483_648, gt=0)


class UserChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str


class UsersActivityGetSchema(BaseModel):
    user_id: str
    username: str
    created_at: str
    times_signed_in: int
    add_money: dict
    times_bought_books: int
    times_returned_books: int
