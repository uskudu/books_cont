from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from app.core.config import settings


engine = create_async_engine(settings.db_url)
new_async_session = async_sessionmaker(bind=engine)

async def get_session():
    async with new_async_session() as session:
        yield session
