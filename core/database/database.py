from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config_reader import config

engine = create_async_engine(
    url=config.URL,
    echo=config.ECHO
)

session_factory = async_sessionmaker(autocommit=False, bind=engine)
