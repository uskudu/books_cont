from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from app.api_v1 import routers
from app.core import settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    try:
        yield
    finally:
        await redis.close()


app = FastAPI(lifespan=lifespan)


for router in routers:
    app.include_router(router)


# @app.on_event("startup")
# async def startup():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
