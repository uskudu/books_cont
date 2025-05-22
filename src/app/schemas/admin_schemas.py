from pydantic import BaseModel, ConfigDict

from app.schemas import BookOwnedSchema
from app.schemas.account_schemas import AccountSchema
from app.schemas.user_schemas import UserActionsGetSchema


class AdminSchema(AccountSchema):
    pass


class AdminSignupSchema(AdminSchema):
    pass


class AdminGetUserActionsSchema(BaseModel):
    user_id: str
    username: str
    money: int
    bought_books: list[BookOwnedSchema]
    actions_history: list[UserActionsGetSchema]

    model_config = ConfigDict(from_attributes=True)


class AdminGetUsersListSchema(BaseModel):
    users: list[AdminGetUserActionsSchema]

    model_config = ConfigDict(from_attributes=True)
