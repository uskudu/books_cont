from datetime import datetime

import redis
from pydantic import BaseModel

redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)


def serialize_to_json(obj):
    if isinstance(obj, BaseModel):
        return serialize_to_json(obj.model_dump())
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (list, tuple)):
        return [serialize_to_json(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize_to_json(value) for key, value in obj.items()}
    return obj

redis_client.delete('users:all')