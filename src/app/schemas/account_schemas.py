from pydantic import BaseModel, ConfigDict


class AccountSchema(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)



class AccountSignupSchema(AccountSchema):
    pass


class AccountSigninSchema(AccountSchema):
    pass
