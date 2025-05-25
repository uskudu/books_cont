from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import uuid

from app.core.config import settings
from app.schemas import UserSchema, AdminSchema

# from app.schemas import AccountSchema

TOKEN_TYPE_FIELD = "token_type"
ACCESS_TOKEN_TYPE = "access"
EXPIRE_MINUTES_PATH = settings.auth_jwt.access_token_expire_minutes


def generate_user_id():
    return str(uuid.uuid4())


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = EXPIRE_MINUTES_PATH,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)

    encoded = jwt.encode(
        to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def create_jwt(
    token_type: str, token_data: dict, expire_minutes: int = EXPIRE_MINUTES_PATH
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
    )


def create_user_access_token(user: UserSchema) -> str:
    jwt_payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=EXPIRE_MINUTES_PATH,
    )


def create_admin_access_token(admin: AdminSchema) -> str:
    jwt_payload = {
        "sub": admin.admin_id,
        "username": admin.username,
        "role": admin.role,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=EXPIRE_MINUTES_PATH,
    )


def hash_password(
    password: str,
) -> str:
    pwd = bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt())
    return pwd.decode("utf-8")


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )
