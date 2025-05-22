from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent.parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 999


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()
    db_url: str = os.getenv("DATABASE_URL")
    db_name: str = os.getenv("POSTGRES_DB")
    redis_url: str = os.getenv("REDIS_URL")


settings = Settings()
