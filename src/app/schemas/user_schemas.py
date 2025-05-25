from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)


class UserSchema(AccountSchema):
    pass


class UserSignupSchema(UserSchema):
    pass


class UserGetVerifiedSchema(UserSchema):
    pass


class UserGetSchema(BaseModel):
    user_id: str
    username: str
    money: int

    model_config = ConfigDict(from_attributes=True)


class UserActionsGetSchema(BaseModel):
    user_id: str
    action_type: str
    details: str
    total: int | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class UserGetSelfSchema(BaseModel):
    user_id: str
    username: str
    money: int
    bought_books: list[BookOwnedSchema] = []

    model_config = ConfigDict(from_attributes=True)


class UserDeleteSchema(BaseModel):
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserAddFundsSchema(BaseModel):
    amount: int = Field(lt=2_147_483_648, gt=0)

    model_config = ConfigDict(from_attributes=True)


class UserAddFundsResponseSchema(BaseModel):
    message: str
    new_balance: int
