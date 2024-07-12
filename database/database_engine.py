from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from core import *

engine = create_async_engine(
    url=app_config.FULL_DB_URL,
    echo=app_config.DB_ECHO
)

session_factory = async_sessionmaker(autocommit=False, bind=engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
