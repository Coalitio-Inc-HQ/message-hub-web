from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core import *

engine = create_async_engine(
    url=app_config.FULL_DB_URL,
    echo=app_config.DB_ECHO
)

session_factory = async_sessionmaker(autocommit=False, bind=engine)
